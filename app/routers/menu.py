from __future__ import annotations
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from app.routers.help import show_main_menu

router = Router(name="menu_compat")

@router.message(Command("menu"))
async def open_menu(m: Message, *_, **__):
    # Прокидываем в единое меню
    await show_main_menu(m)
