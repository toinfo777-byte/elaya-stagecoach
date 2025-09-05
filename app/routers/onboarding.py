from __future__ import annotations

from datetime import datetime
from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart

from app.texts.strings import (
    HELLO,
    CONSENT,
    ONBOARD_GOAL_PROMPT,
    ONBOARD_EXP_PROMPT,
    ONBOARD_TZ_PROMPT,
    ONBOARD_NAME_PROMPT,
)
from app.keyboards.menu import main_menu
from app.storage.repo import session_scope
from app.storage.models import User

router = Router(name="onboarding")


class Onboarding(StatesGroup):
    name = State()
    tz = State()
    goal = State()
    exp = State()
    consent = State()


# ---- вспомогалка: достаём payload из /start ----
def extract_start_payload(text: str | None) -> str | None:
    """
    /start
    /start abc
    /start?start=abc  (Telgram сам превращает в '/start abc' для бота)
    """
    if not text:
        return None
    parts = text.split(maxsplit=1)
    if len(parts) == 2 and parts[0].startswith("/start"):
        return parts[1].strip()
    return None


@router.message(CommandStart())
async def start(msg: Message, state: FSMContext):
    # Сохраняем источник (если пришёл диплинком) в FSM — позже положим в базу, но только если у юзера ещё пусто
    payload = extract_start_payload(msg.text)
    if payload:
        await state.update_data(source=payload[:64])

    await msg.answer(HELLO)
    await msg.answer(ONBOARD_NAME_PROMPT)
    await state.set_state(Onboarding.name)


@router.message(Onboarding.name)
async def set_name(msg: Message, state: FSMContext):
    await state.update_data(name=msg.text.strip())
    await msg.answer(ONBOARD_TZ_PROMPT)
    await state.set_state(Onboarding.tz)


@router.message(Onboarding.tz)
async def set_tz(msg: Message, state: FSMContext):
    await state.update_data(tz=msg.text.strip())
    await msg.answer(ONBOARD_GOAL_PROMPT)
    await state.set_state(Onboarding.goal)


@router.message(Onboarding.goal)
async def set_goal(msg: Message, state: FSMContext):
    await state.update_data(goal=msg.text.strip())
    await msg.answer(ONBOARD_EXP_PROMPT)
    await state.set_state(Onboarding.exp)


@router.message(Onboarding.exp)
async def set_exp(msg: Message, state: FSMContext):
    try:
        exp = int(msg.text.strip())
    except Exception:
        exp = 0
    await state.update_data(exp=exp)
    await msg.answer(CONSENT + "\n\nНапишите «Согласен».")
    await state.set_state(Onboarding.consent)


@router.message(Onboarding.consent)
async def finalize(msg: Message, state: FSMContext):
    data = await state.get_data()

    with session_scope() as s:
        u = s.query(User).filter_by(tg_id=msg.from_user.id).first()
        if not u:
            u = User(tg_id=msg.from_user.id)

        u.username = msg.from_user.username
        u.name = data.get("name")
        u.tz = data.get("tz")
        u.goal = data.get("goal")
        u.exp_level = int(data.get("exp") or 0)
        u.consent_at = datetime.utcnow()

        # ⬇️ ВАЖНО: источник пишем только если он ещё не был установлен раньше
        state_source = (data.get("source") or "").strip() or None
        if not u.source and state_source:
            u.source = state_source[:64]

        s.add(u)

    await state.clear()
    await msg.answer("Готово. Добро пожаловать в меню.", reply_markup=main_menu())
