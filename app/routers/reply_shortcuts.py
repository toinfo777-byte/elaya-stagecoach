# app/routers/reply_shortcuts.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.keyboards.menu import main_menu, small_menu  # у тебя они есть

router = Router(name="reply_shortcuts")

GO_MENU = {"🏠 В меню", "В меню", "/menu", "/start", "Меню"}
GO_SETTINGS = {"⚙️ Настройки", "Настройки", "/settings"}

@router.message(StateFilter("*"), F.text.in_(GO_MENU))
async def go_menu_any_state(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Меню", reply_markup=main_menu())

@router.message(StateFilter("*"), F.text.in_(GO_SETTINGS))
async def go_settings_any_state(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Настройки. Можешь удалить профиль или вернуться в меню.",
        reply_markup=small_menu(),
    )
