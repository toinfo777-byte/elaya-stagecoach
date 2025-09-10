# app/routers/deeplink.py
from __future__ import annotations

from urllib.parse import parse_qs
from aiogram import Router, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.storage.repo import session_scope
from app.storage.models import User
from app.routers.training import training_entry
from app.routers.casting import casting_entry

router = Router(name="deeplink")

def _save_source(user: User | None, src: str | None):
    if not user or not src:
        return
    meta = dict(user.meta_json or {})
    sources = dict(meta.get("sources", {}))
    if "first_source" not in sources:
        sources["first_source"] = src
    sources["last_source"] = src
    meta["sources"] = sources
    user.meta_json = meta

@router.message(StateFilter("*"), CommandStart(deep_link=True))
async def start_deeplink(m: Message, state: FSMContext):
    """Обрабатываем /start <payload>. Поддерживается формат 'go_training&src=xxx' и 'go_casting&src=yyy'."""
    payload = m.text.split(maxsplit=1)[1] if " " in (m.text or "") else ""
    # допускаем формы 'go_training&src=a' и 'start=go_training&src=a'
    qs = payload
    if "=" not in payload and "&" in payload:
        qs = f"start={payload}"
    params = parse_qs(qs, keep_blank_values=True)
    start = (params.get("start") or [""])[0]
    src = (params.get("src") or [""])[0] or None

    # сохраним источник в профиле
    with session_scope() as s:
        u = s.query(User).filter_by(tg_id=m.from_user.id).first()
        if u:
            _save_source(u, src)
            s.add(u)
            s.commit()

    # маршрутизация
    if start == "go_training":
        await training_entry(m, state)
        return
    if start == "go_casting":
        await casting_entry(m, state)
        return

    # по умолчанию обычный /start -> отдаст онбординг в своём роутере
    from app.routers.onboarding import router as _  # no-op, чтобы линтер был счастлив
    await m.answer("Привет! Напиши /menu, чтобы начать.")
