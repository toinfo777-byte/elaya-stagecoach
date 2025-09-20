# app/bot/routers/help.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from app.bot.keyboards.menu import main_menu, BTN_HELP

router = Router(name="help")


@router.message(Command("help"))
@router.message(F.text == BTN_HELP)
async def help_entry(message: Message) -> None:
    """
    Раздел «Помощь». Короткая справка по боту + возврат основного меню.
    """
    text = (
        "<b>Помощь</b>\n\n"
        "• Нажимай кнопки внизу — это основные разделы.\n"
        "• Если что-то «зависло», используй команду /menu — вернёт главное меню.\n"
        "• Команда /start перезапустит онбординг.\n\n"
        "Нужна поддержка? Напиши сюда: @username (замени на свой контакт)."
    )
    await message.answer(text, reply_markup=main_menu(), parse_mode="HTML")
