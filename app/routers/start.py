# app/routers/start.py
from __future__ import annotations

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.keyboards.menu import main_menu
from app.routers.casting import start_casting
from app.routers.training import training_entry

router = Router(name="start")

@router.message(CommandStart(deep_link=True))
async def start_with_deeplink(msg: Message, command: CommandStart.CommandObject):
    arg = (command.args or "").strip()
    if arg.startswith("go_training"):
        return await training_entry(msg)
    if arg.startswith("go_casting"):
        return await start_casting(msg, None)

    await msg.answer(
        "Привет! Я Элайя — тренер сцены. Помогу прокачать голос и уверенность.",
        reply_markup=main_menu()
    )
