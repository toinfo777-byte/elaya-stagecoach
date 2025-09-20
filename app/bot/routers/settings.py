from __future__ import annotations
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from app.keyboards.menu import main_menu, BTN_SETTINGS

router = Router(name="settings")

@router.message(Command("settings"))
@router.message(F.text == BTN_SETTINGS)
async def settings_entry(message: Message) -> None:
    await message.answer(
        "⚙️ <b>Настройки.</b>\nМожешь удалить профиль или вернуться в меню.",
        reply_markup=main_menu()
    )
