# app/routers/reviews.py

from aiogram import Router, F
from aiogram.types import Message

from app.keyboards.main_menu import MAIN_MENU

router = Router(name="reviews-router")

# Эмодзи, с которых может начинаться простой отзыв
EMOJIS = ("⭐", "👍", "🔥", "🥲")


@router.message(F.text)
async def handle_simple_review(message: Message):
    """
    Простой отзыв: один эмодзи + короткая фраза.
    Реагируем только если сообщение начинается с нужного эмодзи.
    Во всех остальных случаях — пропускаем, не ломая другие хендлеры.
    """
    text = message.text or ""
    if not text or text[0] not in EMOJIS:
        return

    await message.answer(
        "Спасибо за отзыв! Я учту это в дальнейшем развитии Элайи 🌕",
        reply_markup=MAIN_MENU,
    )
