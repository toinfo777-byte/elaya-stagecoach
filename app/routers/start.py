# app/routers/start.py
from aiogram import Router, F
from aiogram.types import Message

from app.keyboards.main_menu import MAIN_MENU

router = Router(name="start-router")


@router.message(F.text == "/start")
async def cmd_start(message: Message):
    text = (
        "Привет! Я Элайя — тренер сцены.\n"
        "Помогу прокачать голос, дыхание, уверенность и выразительность.\n\n"
        "Готово! Открываю меню."
    )
    await message.answer(text, reply_markup=MAIN_MENU)
