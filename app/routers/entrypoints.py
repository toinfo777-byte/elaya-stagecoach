from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

router = Router(name="entrypoints")


@router.message(CommandStart())
async def on_start(message: Message) -> None:
    await message.answer(
        "Привет! Я на связи.\n"
        "Доступные команды:\n"
        "• /status — технический статус\n"
        "• /diag — диагностический пинг\n"
        "• /help — справка"
    )


@router.message(Command("help"))
async def on_help(message: Message) -> None:
    await message.answer(
        "Справка:\n"
        "• /status — покажу билд/окружение/uptime\n"
        "• /diag — отправлю диагностический пинг\n"
        "• /sync — (админы) синк с GitHub\n"
        "• /report — (админы) ежедневный отчёт"
    )


@router.message(Command("ping"))
@router.message(Command("diag"))
async def on_ping(message: Message) -> None:
    await message.answer("🏓 pong")
