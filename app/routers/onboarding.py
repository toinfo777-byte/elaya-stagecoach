from __future__ import annotations

from datetime import datetime

from aiogram import Router, F
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram.filters.command import CommandObject

from app.keyboards.menu import main_menu
from app.texts.strings import (
    HELLO,
    CONSENT,
    ONBOARD_GOAL_PROMPT,
    ONBOARD_EXP_PROMPT,
    ONBOARD_TZ_PROMPT,
    ONBOARD_NAME_PROMPT,
)
from app.storage.repo import session_scope
from app.storage.models import User

router = Router(name="onboarding")

# === СТЕЙТЫ ===================================================================
class Onboarding(StatesGroup):
    name = State()
    tz = State()
    goal = State()
    exp = State()
    consent = State()


# === УТИЛИТЫ ==================================================================
def _norm(s: str | None) -> str:
    return (s or "").strip()


def _is_yes_consent(text: str | None) -> bool:
    t = (_norm(text)).lower()
    # принимаем "согласен", "согласна", "согласен.", "согласен!" и т.п.
    return t.startswith("соглас")


def _save_or_update_user(user_id: int, data: dict):
    with session_scope() as s:
        u = s.query(User).filter(User.id == user_id).one_or_none()
        if not u:
            u = User(id=user_id)
            s.add(u)
        u.name = data.get("name") or u.name
        u.tz = data.get("tz") or u.tz
        u.goal = data.get("goal") or u.goal
        u.exp = data.get("exp") or u.exp
        u.source = data.get("source") or u.source
        u.updated_at = datetime.utcnow()
        if not getattr(u, "created_at", None):
            u.created_at = datetime.utcnow()
        s.flush()


# === ХЭНДЛЕРЫ =================================================================
@router.message(StateFilter(None), CommandStart(deep_link=True))
async def start(msg: Message, state: FSMContext, command: CommandObject):
    # payload из deep link (/start <payload>)
    payload = (command.args or "").strip() if command else ""
    if payload:
        # Сохраняем в FSM — используем после онбординга (роутинг в модуль)
        await state.update_data(start_payload=payload)

    await msg.answer(HELLO)
    await msg.answer(ONBOARD_NAME_PROMPT)
    await state.set_state(Onboarding.name)


@router.message(~StateFilter(None), Command("cancel"))
async def cancel_anywhere(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer("Анкета сброшена. Возвращаю в меню.", reply_markup=main_menu())


@router.message(~StateFilter(None), Command("menu"))
async def menu_anywhere(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer("Готово. Вот меню:", reply_markup=main_menu())


# Блокируем ТОЛЬКО slash-команды во время анкеты (чтобы нижнее меню работало).
@router.message(~StateFilter(None), F.text.startswith("/"))
async def in_form_but_command(msg: Message):
    await msg.answer("Вы сейчас заполняете короткую анкету. Напишите ответ или /cancel, чтобы выйти.")


# === ШАГИ ФОРМЫ ==============================================================

@router.message(Onboarding.name, F.text.len() > 0)
async def set_name(msg: Message, state: FSMContext):
    await state.update_data(name=_norm(msg.text))
    await msg.answer(ONBOARD_TZ_PROMPT)
    await state.set_state(Onboarding.tz)


@router.message(Onboarding.tz, F.text.len() > 0)
async def set_tz(msg: Message, state: FSMContext):
    await state.update_data(tz=_norm(msg.text))
    await msg.answer(ONBOARD_GOAL_PROMPT)
    await state.set_state(Onboarding.goal)


@router.message(Onboarding.goal, F.text.len() > 0)
async def set_goal(msg: Message, state: FSMContext):
    await state.update_data(goal=_norm(msg.text))
    await msg.answer(ONBOARD_EXP_PROMPT)
    await state.set_state(Onboarding.exp)


@router.message(Onboarding.exp, F.text.len() > 0)
async def set_exp(msg: Message, state: FSMContext):
    await state.update_data(exp=_norm(msg.text))
    await msg.answer(CONSENT)
    await state.set_state(Onboarding.consent)


@router.message(Onboarding.consent, F.text.func(_is_yes_consent))
async def finalize(msg: Message, state: FSMContext):
    data = await state.get_data()
    # Сохраняем пользователя
    _save_or_update_user(msg.from_user.id, data | {"source": data.get("start_payload", "")})

    await state.clear()
    await msg.answer("Готово! Открываю меню.", reply_markup=main_menu())

    # Если пришли по deep-link — отправим дальше
    payload = data.get("start_payload", "")
    if payload:
        # Простые маршруты:
        if payload.startswith("go_training"):
            await msg.answer("Запускаю тренировку дня…")
            # эмулируем нажатие команды/кнопки (зависит от твоей реализации)
            await msg.bot.send_message(msg.chat.id, "Тренировка дня")
        elif payload.startswith("go_casting"):
            await msg.answer("Открою мини-кастинг…")
            await msg.bot.send_message(msg.chat.id, "Мини-кастинг")
        # добавляй свои варианты: go_training_post_XXXX, go_casting_post_YYYY, и т.д.


@router.message(Onboarding.consent)
async def ask_consent_again(msg: Message):
    await msg.answer("Пожалуйста, напишите «Согласен» (или /cancel, чтобы выйти).")
