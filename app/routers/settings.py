from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.keyboards.menu import small_menu

router = Router(name="settings")

@router.message(Command("settings"))
async def show_settings(m: Message):
    await m.answer("Настройки. Можешь удалить профиль или вернуться в меню.", reply_markup=small_menu())
