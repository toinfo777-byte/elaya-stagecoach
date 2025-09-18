from __future__ import annotations

from aiogram import Router, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from sqlalchemy import select, desc

from app.keyboards.menu import main_menu
from app.storage.repo import session_scope
from app.storage.models import User, Lead
from app.utils.textmatch import contains_ci

router = Router(name="apply")


# === FSM ======================================================================

class ApplyStates(StatesGroup):
    waiting_text = State()


def _kb_apply_menu() -> ReplyKeyboardMarkup:
    rows = [
        [KeyboardButton(text="✍️ Изменить заявку")],
        [KeyboardButton(text="🧭 В меню")],
    ]
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True, is_persistent=True)


# === Хэндлеры =================================================================

@router.message(F.text.func(contains_ci("путь лидера")))
@router.message(F.text == "/apply")
async def apply_entry(m: Message, state: FSMContext, user: User) -> None:
    """Попросить короткую цель одним сообщением."""
    await state.set_state(ApplyStates.waiting_text)
    text = (
        "Путь лидера: короткая заявка.\n"
        "Напишите, чего хотите достичь — одним сообщением."
    )
    await m.answer(text)


@router.message(ApplyStates.waiting_text, F.text.len() > 1)
async def apply_save(m: Message, state: FSMContext, user: User) -> None:
    """Сохраняем текст заявки как lead и показываем подтверждение."""
    text = (m.text or "").strip()

    contact = f"@{m.from_user.username}" if (m.from_user and m.from_user.username) else str(m.from_user.id if m.from_user else user.tg_id)

    with session_scope() as s:
        lead = Lead(
            user_id=user.id,
            channel="tg",
            contact=contact,
            note=text,
            track=None,
        )
        s.add(lead)

    await state.clear()

    await m.answer("Спасибо! Принял. Двигаемся дальше 👍", reply_markup=_kb_apply_menu())


@router.message(F.text.func(contains_ci("изменить заявку")))
async def apply_edit(m: Message, state: FSMContext, user: User) -> None:
    """Переводим обратно в режим ввода новой заявки."""
    await state.set_state(ApplyStates.waiting_text)
    await m.answer("Отправьте новый вариант одним сообщением.")


@router.message(F.text.func(contains_ci("в меню")))
async def apply_back_to_menu(m: Message, state: FSMContext, user: User) -> None:
    await state.clear()
    await m.answer("Готово. Добро пожаловать в меню.", reply_markup=main_menu())
