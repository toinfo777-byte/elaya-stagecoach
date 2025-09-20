from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from app.keyboards.menu import main_menu, get_bot_commands, BTN_HELP

router = Router(name="help")


@router.message(Command("help"))
@router.message(F.text == BTN_HELP)
async def help_entry(message: Message) -> None:
    cmds = get_bot_commands()
    lines = ["<b>Команды:</b>"]
    for c in cmds:
        lines.append(f"/{c.command} — {c.description}")
    await message.answer("\n".join(lines), reply_markup=main_menu())
