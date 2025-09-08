# app/routers/progress.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message

from app.keyboards.menu import main_menu
from app.storage.repo import session_scope
from app.storage.models import User, DrillRun, Drill, TestResult, Lead  # <-- + Lead

router = Router(name="progress")

SPARK = "▁▂▃▄▅▆▇█"


def spark(value: int) -> str:
    idx = max(0, min(7, round((value or 0) * 7 / 5)))
    return SPARK[idx]


@router.message(StateFilter("*"), F.text == "📈 Мой прогресс")
@router.message(StateFilter("*"), Command("progress"))
@router.message(StateFilter("*"), lambda m: isinstance(m.text, str) and "прогресс" in m.text.lower())
async def show_progress(m: Message):
    with session_scope() as s:
        u = s.query(User).filter_by(tg_id=m.from_user.id).first()
        if not u:
            await m.answer("Сначала /start.", reply_markup=main_menu())
            return

        # есть ли заявка в «Путь лидера»
        has_leader = s.query(Lead).filter_by(user_id=u.id, track="leader").first() is not None

        # последние 3 прогона
        runs = (
            s.query(DrillRun)
            .filter_by(user_id=u.id)
            .order_by(DrillRun.ts.desc())
            .limit(3)
            .all()
        )

        # тайтлы этюдов
        last: list[str] = []
        for r in runs:
            d = s.query(Drill).filter_by(id=r.drill_id).first()
            if d:
                last.append(d.payload_json.get("title", r.drill_id))

        # профиль по последнему тесту
        tr: TestResult | None = (
            s.query(TestResult)
            .filter_by(user_id=u.id)
            .order_by(TestResult.ts.desc())
            .first()
        )

    axes_txt = (
        "нет данных (пройдите 🎭 Мини-кастинг)"
        if not tr
        else "Внимание {0} {5}\nПауза {1} {6}\nТемп {2} {7}\nИнтонация {3} {8}\nЛогика {4} {9}".format(
            tr.axes_json.get("attention", 0),
            tr.axes_json.get("pause", 0),
            tr.axes_json.get("tempo", 0),
            tr.axes_json.get("intonation", 0),
            tr.axes_json.get("logic", 0),
            spark(tr.axes_json.get("attention", 0)),
            spark(tr.axes_json.get("pause", 0)),
            spark(tr.axes_json.get("tempo", 0)),
            spark(tr.axes_json.get("intonation", 0)),
            spark(tr.axes_json.get("logic", 0)),
        )
    )

    # заголовок с бейджами
    header: list[str] = []
    if getattr(u, "source", None):
        header.append(f"Источник: {u.source}")
    if has_leader:
        header.append("Трек: Лидер (waitlist)")
    header_txt = "\n".join(header)

    last_txt = "— нет записей" if not last else "• " + "\n• ".join(last)
    streak = getattr(u, "streak", 0) or 0

    body = (
        f"Стрик: {streak}\n\n"
        f"Последние этюды:\n{last_txt}\n\n"
        f"Профиль 5 осей:\n{axes_txt}"
    )
    msg = (header_txt + "\n\n" + body) if header_txt else body

    await m.answer(msg, reply_markup=main_menu())
