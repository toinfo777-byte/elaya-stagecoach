# app/routers/onboarding.py
from __future__ import annotations

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.keyboards.reply import main_menu_kb

router = Router(name="onboarding")

@router.message(CommandStart())
async def start(m: Message) -> None:
    """Онбординг: приветствие + сразу показываем главное меню."""
    await m.answer(
        "Привет! Я Элайя — тренер сцены. Ниже — главное меню:",
        reply_markup=main_menu_kb(),
    )
