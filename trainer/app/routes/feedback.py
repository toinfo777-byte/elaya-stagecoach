from __future__ import annotations

from aiogram import Router, F
from aiogram.types import Message

from app.keyboards.main_menu import MAIN_MENU

router = Router(name="feedback")

THANKS_TEXT = (
    "Спасибо за отзыв.\n"
    "Я его учту и буду становиться лучше."
)


@router.message(F.text)
async def handle_feedback(message: Message) -> None:
    """
    Пока работаем без базы: просто принимаем текст и отвечаем.
    Если захочется — позже привяжем сюда регистрацию в training_progress.
    """
    # text = message.text.strip()  # можно логировать при желании
    await message.answer(THANKS_TEXT, reply_markup=MAIN_MENU)
