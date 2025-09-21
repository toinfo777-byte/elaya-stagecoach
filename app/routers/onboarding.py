from __future__ import annotations

from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from app.keyboards.menu import main_menu

router = Router(name="onboarding")

# /start БЕЗ payload'а — открываем меню
@router.message(CommandStart(deep_link=False))
async def start_plain(m: Message) -> None:
    await m.answer("Готово! Открываю меню.", reply_markup=main_menu())

# Ручная команда на всякий случай
@router.message(Command("menu"))
async def cmd_menu(m: Message) -> None:
    await m.answer("Меню", reply_markup=main_menu())
