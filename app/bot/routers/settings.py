# app/bot/routers/settings.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from app.bot.keyboards.menu import main_menu, BTN_SETTINGS

router = Router(name="settings")


@router.message(Command("settings"))
@router.message(F.text == BTN_SETTINGS)
async def settings_entry(message: Message) -> None:
    """
    Раздел «Настройки». Делаем его максимально простым — всё через команды.
    """
    text = (
        "⚙️ <b>Настройки</b>\n\n"
        "• Удалить профиль и записи — /wipe_me\n"
        "• Вернуться в главное меню — /menu\n\n"
        "Если нужно что-то ещё — напиши в поддержку."
    )
    await message.answer(text, reply_markup=main_menu(), parse_mode="HTML")
