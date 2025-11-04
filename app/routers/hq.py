# app/routers/hq.py
from __future__ import annotations
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router(name="hq")

@router.message(Command("menu"))
async def cmd_menu(m: Message):
    await m.answer(
        "📋 HQ-меню:\n"
        "• /status — состояние\n"
        "• /webhookinfo — инфо по вебхуку\n"
        "• /healthz — пинг"
    )
