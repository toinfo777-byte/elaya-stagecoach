# app/routers/diag.py
from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

# Глобальный aiogram-роутер бота.
bot_router = Router(name="diag")


@bot_router.message(Command("ping"))
async def cmd_ping(message: Message) -> None:
    await message.answer("pong")


def get_router() -> Router:
    """
    Совместимость: если где-то ожидают фабрику — вернём тот же router.
    """
    return bot_router
