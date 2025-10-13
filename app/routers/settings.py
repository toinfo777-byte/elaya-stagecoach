from __future__ import annotations
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

settings_router = Router(name="settings")

@settings_router.message(Command("settings"))
@settings_router.message(F.text.casefold().in_({"⚙️ настройки", "настройки", "settings"}))
async def show_settings(m: Message):
    await m.answer(
        "⚙️ <b>Настройки</b>\n\n"
        "Персональные параметры появятся позже.\n"
        "Пока можно пользоваться базовым меню: /menu"
    )
