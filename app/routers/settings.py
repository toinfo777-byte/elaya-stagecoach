# app/routers/settings.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext

from app.keyboards.menu import main_menu
from app.storage.repo import delete_user  # функция очистки профиля по tg_id

router = Router(name="settings")


def settings_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [KeyboardButton(text="🏠 В меню")],
            [KeyboardButton(text="🗑 Удалить профиль")],
        ],
    )


@router.message(F.text == "⚙️ Настройки")
@router.message(F.text == "/settings")
async def settings_entry(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer(
        "⚙️ Настройки. Можешь удалить профиль или вернуться в меню.",
        reply_markup=settings_kb()
    )


@router.message(F.text == "🗑 Удалить профиль")
async def settings_delete(msg: Message, state: FSMContext):
    await state.clear()
    await delete_user(msg.from_user.id)
    await msg.answer(
        "🗑 Профиль удалён. Открываю меню.",
        reply_markup=main_menu()
    )


@router.message(F.text == "🏠 В меню")
async def settings_to_menu(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer(
        "Готово! Открываю меню.",
        reply_markup=main_menu()
    )
