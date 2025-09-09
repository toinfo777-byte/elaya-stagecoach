# app/routers/deeplink.py
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.storage.repo import session_scope
from app.storage.models import User
from app.routers.training import training_entry
from app.routers.casting import casting_entry  # см. ниже хендлер
from app.routers.coach import coach_on_cmd     # см. ниже хендлер

router = Router(name="deeplink")

def _remember_first_source(user_id: int, source: str):
    with session_scope() as s:
        u = s.query(User).filter_by(tg_id=user_id).first()
        if not u:
            return
        if not u.first_source:
            u.first_source = source
        u.last_source = source
        s.commit()

@router.message(CommandStart(deep_link=True))
async def start_with_payload(m: Message, state: FSMContext, command: CommandStart):
    payload = (command.args or "").strip()
    if not payload:
        return  # обычный /start отработает в onboarding

    # запомним источник однократно + как last_source
    _remember_first_source(m.from_user.id, payload)

    if payload == "go_training":
        await training_entry(m, state)
        return

    if payload == "go_casting":
        await casting_entry(m, state)
        return

    if payload in {"coach", "go_coach"}:
        await coach_on_cmd(m)
        return

    # на неизвестный payload — просто привет
    await m.answer("Привет! Готов?")
