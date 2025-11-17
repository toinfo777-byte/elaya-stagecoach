# app/routers/reviews.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.types import Message

from app.keyboards.main_menu import MAIN_MENU

router = Router(name="reviews-router")


@router.message(F.text.regexp(r"^⭐|^👍|^🔥|^💡"))
async def handle_simple_review(message: Message) -> None:
    """
    Базовый сценарий отзывов.

    Ловим любое сообщение, которое начинается с одного из эмодзи:
    ⭐ / 👍 / 🔥 / 💡

    Примеры:
    - "⭐ Очень крутой бот"
    - "🔥"
    - "💡 Можно добавить больше упражнений"
    """
    await message.answer(
        "Спасибо за отзыв! Я учту это в дальнейшем развитии Элайи 🌕",
        reply_markup=MAIN_MENU,
    )
