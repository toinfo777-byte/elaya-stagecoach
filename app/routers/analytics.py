from __future__ import annotations

import os
from datetime import datetime, timedelta
from collections import defaultdict

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from sqlalchemy import inspect as sqla_inspect
from sqlalchemy.sql.sqltypes import DateTime, Date

from app.storage.repo import session_scope
from app.storage.models import User, DrillRun

# Event модель может называться по-разному — попробуем импортировать безопасно
try:
    from app.storage.models import Event  # type: ignore
except Exception:  # в некоторых проектах событие называется MetricEvent
    Event = None  # type: ignore[misc,assignment]

router = Router(name="analytics")


# ——— простейшая проверка админа ———
def _admin_ids() -> set[int]:
    # 1) из settings.ADMIN_IDS
    try:
        from app.config import settings  # type: ignore
        ids = getattr(settings, "ADMIN_IDS", None)
        if ids:
            # допускаем как список, так и строку с запятыми
            if isinstance(ids, (list, tuple, set)):
                return {int(x) for x in ids}
            if isinstance(ids, str):
                return {int(x) for x in ids.split(",") if x.strip()}
    except Exception:
        pass
    # 2) из ENV
    env = os.getenv("ADMIN_IDS") or os.getenv("ADMIN_TG_IDS") or ""
    return {int(x) for x in env.replace(";", ",").split(",") if x.strip().isdigit()}


def _is_admin(uid: int) -> bool:
    ids = _admin_ids()
    return not ids or uid in ids  # если список не задан — не режем доступ (dev)


# ——— /traffic [days] — агрегированный отчёт по источникам ———
@router.message(Command("traffic"))
async def traffic_report(m: Message):
    if not _is_admin(m.from_user.id):
        return

    # количество дней можно передать через /traffic 7
    try:
        parts = (m.text or "").strip().split()
        days = int(parts[1]) if len(parts) > 1 else 7
    except Exception:
        days = 7
    since = datetime.utcnow() - timedelta(days=days)

    with session_scope() as s:
        # пользователи по источнику
        users = s.query(User).all()
        by_src_users_total = defaultdict(int)
        by_src_new_since = defaultdict(int)
        for u in users:
            src = (u.source or "—")
            by_src_users_total[src] += 1
            try:
                if getattr(u, "consent_at", None) and u.consent_at >= since:
                    by_src_new_since[src] += 1
            except Exception:
                pass

        # активности тренировок
        by_src_started = defaultdict(int)
        by_src_finished = defaultdict(int)

        mapper = sqla_inspect(DrillRun)
        dt_col = next((c for c in mapper.columns if isinstance(c.type, (DateTime, Date))), None)

        q = s.query(DrillRun).join(User, DrillRun.user_id == User.id)
        if dt_col is not None:
            q = q.filter(dt_col >= since)
        runs = q.all()
        for r in runs:
            # считаем start/finish приблизительно по success_bool
            src = (getattr(r, "user", None).source if hasattr(r, "user") and r.user else None)  # type: ignore
            if src is None:
                # запасной путь — второй запрос брать не будем; просто поставим "—"
                src = "—"
            by_src_started[src] += 1
            try:
                if getattr(r, "success_bool", None):
                    by_src_finished[src] += 1
            except Exception:
                pass

        # заявки на премиум из событий (если есть Event)
        by_src_premium = defaultdict(int)
        if Event is not None:
            # ищем события типа "premium_interest" за период
            ev_mapper = sqla_inspect(Event)
            ev_dt = next((c for c in ev_mapper.columns if isinstance(c.type, (DateTime, Date))), None)
            ev_q = s.query(Event).join(User, Event.user_id == User.id).filter(getattr(Event, "event", None) == "premium_interest")
            if ev_dt is not None:
                ev_q = ev_q.filter(ev_dt >= since)
            for ev in ev_q.all():
                try:
                    src = ev.user.source if hasattr(ev, "user") and ev.user else "—"  # type: ignore[attr-defined]
                except Exception:
                    src = "—"
                by_src_premium[src] += 1

    # нормализуем полный список источников
    sources = sorted(set().union(
        by_src_users_total.keys(),
        by_src_new_since.keys(),
        by_src_started.keys(),
        by_src_finished.keys(),
        by_src_premium.keys(),
    ), key=lambda x: (x == "—", x))

    # собираем текст отчёта
    lines = [
        f"📊 <b>Трафик по источникам</b> (за {days} дн.)",
        "Источник | Новые | Всего | Старт трен. | Финиш трен. | Заявки ⭐️",
        "—"*60,
    ]
    for src in sources:
        new_ = by_src_new_since.get(src, 0)
        total = by_src_users_total.get(src, 0)
        st = by_src_started.get(src, 0)
        fin = by_src_finished.get(src, 0)
        pm = by_src_premium.get(src, 0)
        lines.append(f"{src} | {new_} | {total} | {st} | {fin} | {pm}")

    lines.append("\nПодсказка: генерируй диплинки вида <code>https://t.me/<bot>?start=src_vc_sep</code>")
    await m.answer("\n".join(lines))


# ——— /dl <код> — быстро получить диплинк на этого бота с payload ———
@router.message(Command("dl"))
async def make_deeplink(m: Message):
    if not _is_admin(m.from_user.id):
        return
    parts = (m.text or "").split(maxsplit=1)
    payload = parts[1].strip() if len(parts) == 2 else "src_demo"
    me = await m.bot.get_me()
    link = f"https://t.me/{me.username}?start={payload}"
    await m.answer(f"🔗 <b>Диплинк</b> для кода <code>{payload}</code>:\n{link}")
