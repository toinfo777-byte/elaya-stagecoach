from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from app.keyboards.menu import get_bot_commands, main_menu

router = Router(name="help")

@router.message(Command("help"))
async def help_cmd(message: Message) -> None:
    cmds = get_bot_commands()
    txt = ["<b>Команды:</b>"]
    for c in cmds:
        txt.append(f"/{c.command} — {c.description}")
    await message.answer("\n".join(txt), reply_markup=main_menu())
