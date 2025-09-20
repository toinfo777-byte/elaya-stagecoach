from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from app.bot.keyboards.menu import main_menu

router = Router(name="system")

@router.message(Command("menu"))
@router.message(F.text.in_({"В меню", "/menu"}))
async def back_to_menu(message: Message) -> None:
    await message.answer("Ок, вернулись в главное меню. Нажми нужную кнопку снизу.", reply_markup=main_menu())
