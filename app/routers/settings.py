# app/routers/settings.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from app.keyboards.menu import small_menu, main_menu, BTN_SETTINGS

router = Router(name="settings")


@router.message(F.text == BTN_SETTINGS)
@router.message(Command("settings"))
async def settings_entry(m: Message) -> None:
    await m.answer("Настройки. Можешь удалить профиль или вернуться в меню.", reply_markup=small_menu())
