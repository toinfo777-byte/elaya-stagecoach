# app/routers/system.py
from __future__ import annotations

from aiogram import Router, types
from aiogram.filters import CommandStart

from app.config import settings

router = Router(name="system")


@router.message(CommandStart())
async def cmd_start(message: types.Message):
    if settings.bot_profile == "hq":
        # Никаких клавиатур — просто лаконичный текст
        await message.answer(
            "Привет! Я HQ-бот. Готов принимать команды статуса и оповещений."
        )
        return

    # Профиль trainer — показываем меню (как у тебя было)
    kb = ...  # твоя клавиатура тренера
    await message.answer("Меню тренировки:", reply_markup=kb)
