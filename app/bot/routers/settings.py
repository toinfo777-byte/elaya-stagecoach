from __future__ import annotations
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from app.keyboards.menu import main_menu, BTN_SETTINGS

router = Router(name="settings")

@router.message(Command("settings"))
@router.message(F.text == BTN_SETTINGS)
async def settings_entry(message: Message) -> None:
    text = (
        "<b>Настройки</b>.\n"
        "Можешь удалить профиль или вернуться в меню.\n\n"
        "Чтобы полностью удалить данные — отправь команду <code>/wipe_me</code>."
    )
    await message.answer(text, reply_markup=main_menu())
