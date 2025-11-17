# app/routers/reviews.py
from aiogram import Router
from aiogram.types import Message

from app.keyboards.main_menu import MAIN_MENU

router = Router(name="reviews-router")

EMOJIS = ("⭐", "👍", "🔥", "😍", "🤩")

@router.message()
async def handle_simple_review(message: Message):
    text = message.text or ""

    # реагируем только если начинается с нужного эмодзи
    if not text or text[0] not in EMOJIS:
        return

    await message.answer(
        "Спасибо за отзыв! Я учту это в дальнейшем развитии Элайи 🧡",
        reply_markup=MAIN_MENU,
    )
