from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from app.keyboards.menu import main_menu, BTN_CASTING

router = Router(name="casting")

def _quiz_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Факт", callback_data="cast:fact")],
        [InlineKeyboardButton(text="Манипуляция", callback_data="cast:manip")],
    ])

@router.message(Command("casting"))
@router.message(F.text == BTN_CASTING)
async def casting_entry(message: Message) -> None:
    await message.answer("🎭 Мини-кастинг", reply_markup=main_menu())
    await message.answer(
        "Вопрос 1/10:\nВысказывание похоже на факт или на манипуляцию?",
        reply_markup=_quiz_keyboard(),
    )

from aiogram.types import CallbackQuery

@router.callback_query(F.data.startswith("cast:"))
async def casting_answer(cb: CallbackQuery) -> None:
    await cb.answer("Ответ принят")
    await cb.message.edit_reply_markup()  # убрали кнопки на этом вопросе
    # Опционально – можно отправить следующий вопрос
