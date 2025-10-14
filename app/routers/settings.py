# app/routers/settings.py
from __future__ import annotations
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router(name="settings")

@router.message(Command("settings"))
async def show_settings(m: Message):
    await m.answer(
        "⚙️ Настройки\n\n"
        "Функция пока недоступна.\n"
        "Позже здесь можно будет выбрать язык, уведомления и темы."
    )

__all__ = ["router", "show_settings"]
