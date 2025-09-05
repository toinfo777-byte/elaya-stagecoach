# app/routers/onboarding.py
from datetime import datetime
from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart
from aiogram.filters.command import CommandObject  # <-- чтобы получить payload /start

from app.texts.strings import (
    HELLO, CONSENT,
    ONBOARD_GOAL_PROMPT, ONBOARD_EXP_PROMPT,
    ONBOARD_TZ_PROMPT, ONBOARD_NAME_PROMPT
)
from app.keyboards.menu import main_menu
from app.storage.repo import session_scope
from app.storage.models import User


class Onboarding(StatesGroup):
    name = State()
    tz = State()
    goal = State()
    exp = State()
    consent = State()


router = Router(name="onboarding")


@router.message(CommandStart())
async def start(msg: Message, state: FSMContext, command: CommandObject):
    """
    Старт онбординга. Если пришёл диплинк вида
    t.me/<bot>?start=<payload>, сохраняем payload как источник.
    """
    payload = (command.args or "").strip() if command else ""
    if payload:
        # кладём в FSM и (если профиль уже есть) пишем сразу в БД, не перезаписывая
        await state.update_data(source=payload[:64])
        with session_scope() as s:
            u = s.query(User).filter_by(tg_id=msg.from_user.id).first()
            if u and not getattr(u, "source", None):
                u.source = payload[:64]
