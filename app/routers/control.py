# app/routers/control.py
from __future__ import annotations

import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command

router = Router(name=__name__)
log = logging.getLogger("control")

@router.message(CommandStart())
async def on_start(msg: Message):
    await msg.answer(
        "Привет! Я живой. Команды: /ping, /help"
    )

@router.message(Command("help"))
async def on_help(msg: Message):
    await msg.answer("Доступно: /ping — проверить ответ бота.")

@router.message(Command("ping"))
async def on_ping(msg: Message):
    await msg.answer("pong")
