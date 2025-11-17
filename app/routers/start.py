# app/routers/start.py

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.keyboards.main_menu import MAIN_MENU

router = Router(name="start-router")


@router.message(CommandStart())
async def cmd_start(message: Message):
    text = (
        "Привет! Я Элайя — тренер сцены.\n\n"
        "Помогу прокачать голос, дыхание, уверенность и выразительность.\n"
        "Выбери, с чего начнём 👇"
    )
    await message.answer(text, reply_markup=MAIN_MENU)
