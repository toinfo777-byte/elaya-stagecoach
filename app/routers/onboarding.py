from __future__ import annotations

from datetime import datetime
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters.state import StateFilter
from aiogram.types import Message

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


def extract_start_payload(text: str | None) -> str | None:
    """
    /start
    /start abc
    Telegram сам превращает deep-link "?start=abc" в строку '/start abc'
    """
    if not text:
        return None
    parts = text.split(maxsplit=1)
    if len(parts) == 2 and parts[0].startswith("/start"):
        return parts[1].strip()
    return None


# --- старт онбординга: только если нет активного состояния ---
@router.message(StateFilter(None), CommandStart())
async def start(msg: Message, state: FSMContext):
    payload = extract_start_payload(msg.text)
    if payload:
        await state.update_data(source=payload[:64])

    await msg.answer(HELLO)
    await msg.answer(ONBOARD_NAME_PROMPT)
    await state.set_state(Onboarding.name)


# --- /cancel: позволяет выйти из анкеты в любой момент ---
@router.message(~StateFilter(None), Command("cancel"))
async def cancel_anywhere(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer("Анкета сброшена. Возвращаю в меню.", reply_markup=main_menu())


# --- если юзер в анкете и жмёт команды, не ломаемся ---
@router.message(~StateFilter(None), F.text.startswith("/"))
async def in_form_but_command(msg: Message):
    await msg.answer("Вы сейчас заполняете короткую анкету. Напишите ответ или /cancel, чтобы выйти.")


# === шаги анкеты: принимаем ТОЛЬКО обычный текст, не команды ===

@router.message(Onboarding.name, ~F.text.startswith("/"))
async def set_name(msg: Message, state: FSMContext):
    await state.update_data(name=(msg.text or "").strip())
    await msg.answer(ONBOARD_TZ_PROMPT)
    await state.set_state(Onboarding.tz)


@router.message(Onboarding.tz, ~F.text.startswith("/"))
async def set_tz(msg: Message, state: FSMContext):
    await state.update_data(tz=(msg.text or "").strip())
    await msg.answer(ONBOARD_GOAL_PROMPT)
    await state.set_state(Onboarding.goal)


@router.message(Onboarding.goal, ~F.text.startswith("/"))
async def set_goal(msg: Message, state: FSMContext):
    await state.update_data(goal=(msg.text or "").strip())
    await msg.answer(ONBOARD_EXP_PROMPT)
    await state.set_state(Onboarding.exp)


@router.message(Onboarding.exp, ~F.text.startswith("/"))
async def set_exp(msg: Message, state: FSMContext):
    try:
        exp = int((msg.text or "").strip())
    except Exception:
        exp = 0
    await state.update_data(exp=exp)
    await msg.answer(CONSENT + "\n\nНапишите «Согласен».")
    await state.set_state(Onboarding.consent)


@router.message(Onboarding.consent, ~F.text.startswith("/"))
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

        src = (data.get("source") or "").strip() or None
        if not u.source and src:
            u.source = src[:64]

        s.add(u)

    await state.clear()
    await msg.answer("Готово. Добро пожаловать в меню.", reply_markup=main_menu())
