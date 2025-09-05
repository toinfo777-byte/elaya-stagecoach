# app/routers/help.py
from aiogram import Router, types
from aiogram.filters import Command
from app.keyboards.menu import main_menu
from app.texts.strings import HELP  # используем тот же текст, без разметки

router = Router(name="help_fallback")

@router.message(Command("help"))
async def help_cmd(m: types.Message):
    # Без parse_mode → Telegram не парсит Markdown, ошибки не будет
    await m.answer(HELP, reply_markup=main_menu())
