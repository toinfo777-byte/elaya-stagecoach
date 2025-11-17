# app/routers/reviews.py
from aiogram import Router, F
from aiogram.types import Message

from app.keyboards.main_menu import MAIN_MENU

router = Router(name="reviews-router")


@router.message(F.text.regexp(r"^⭐|^👍|^🔥|^💡"))  # временно, потом сделаем нормальный сценарий
async def handle_simple_review(message: Message):
    """
    Временная заглушка:
    пользователь может отправить эмодзи + короткий текст в одном сообщении.
    Во вторник сделаем полноценный сценарий: сначала эмодзи, потом спрашиваем фразу.
    """
    await message.answer(
        "Спасибо за отзыв! Я учту это в дальнейшем развитии Элайи 🌕",
        reply_markup=MAIN_MENU,
    )
