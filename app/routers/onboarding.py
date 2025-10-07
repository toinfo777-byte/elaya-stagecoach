from __future__ import annotations
from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from app.routers.help import show_main_menu

router = Router(name="onboarding")

@router.message(CommandStart(deep_link=False))
async def start_plain(m: Message) -> None:
    await show_main_menu(m)

@router.message(Command("menu"))
async def cmd_menu(m: Message) -> None:
    await show_main_menu(m)
