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


# === ВСПОМОГАТЕЛЬНОЕ ==========================================================
def _norm(s: str | None) -> str:
    return (s or "").strip()

def _is_yes_consent(text: str | None) -> bool:
    t = (_norm(text)).lower()
    return t.startswith("соглас")  # «согласен», «согласна», с точками/эмодзи — ок

def _get_user(user_id: int) -> User | None:
    with session_scope() as s:
        return s.query(User).filter(User.id == user_id).one_or_none()

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
        if "start_payload" in data and data["start_payload"]:
            u.source = data["start_payload"]
        u.updated_at = datetime.utcnow()
        if not getattr(u, "created_at", None):
            u.created_at = datetime.utcnow()
        s.flush()

async def _route_by_payload(msg: Message, payload: str):
    """
    Простая маршрутизация после старта по ссылке:
      go_training*  -> в тренировку
      go_casting*   -> в мини-кастинг
    """
    p = payload.strip()
    if p.startswith("go_training"):
        await msg.answer("Запускаю тренировку дня…")
        # В реальном проекте вместо ответа можно триггерить нужный хэндлер
        await msg.bot.send_message(msg.chat.id, "Тренировка дня")
    elif p.startswith("go_casting"):
        await msg.answer("Открою мини-кастинг…")
        await msg.bot.send_message(msg.chat.id, "Мини-кастинг")
    else:
        # неизвестный payload — просто открываем меню
        await msg.answer("Готово. Вот меню:", reply_markup=main_menu())


# === ХЭНДЛЕРЫ =================================================================

# ЕДИНСТВЕННАЯ точка входа для /start (и с payload).
@router.message(StateFilter(None), CommandStart(deep_link=True))
async def start(msg: Message, state: FSMContext, command: CommandObject):
    payload = (command.args or "").strip() if command else ""
    existing = _get_user(msg.from_user.id)

    if existing:
        # Профиль уже есть → deep-link ведём сразу
        if payload:
            await _route_by_payload(msg, payload)
            return
        # Без payload — просто меню
        await msg.answer("Готово. Вот меню.", reply_markup=main_menu())
        return

    # Профиля нет → начинаем онбординг. Запомним payload, чтобы дороутить потом.
    if payload:
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


# Блокируем ТОЛЬКО slash-команды во время анкеты (нижнее меню/эмодзи не трогаем)
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
    _save_or_update_user(msg.from_user.id, data)

    await state.clear()
    await msg.answer("Готово! Открываю меню.", reply_markup=main_menu())

    # Если стартовали по ссылке — дороутим
    payload = data.get("start_payload", "")
    if payload:
        await _route_by_payload(msg, payload)


@router.message(Onboarding.consent)
async def ask_consent_again(msg: Message):
    await msg.answer("Пожалуйста, напишите «Согласен» (или /cancel, чтобы выйти).")
