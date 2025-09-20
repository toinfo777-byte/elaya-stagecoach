from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from app.bot.keyboards.menu import main_menu_kb

router = Router(name="system")


# Открыть главное меню
@router.message(Command("menu"))
@router.message(F.text.in_({"Меню", "В меню", "📎 В меню"}))
async def open_menu(message: Message) -> None:
    await message.answer("Ок, вернулись в главное меню. Нажми нужную кнопку снизу.", reply_markup=main_menu_kb())
