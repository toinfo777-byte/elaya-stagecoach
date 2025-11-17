# app/routers/progress.py
from aiogram import Router, F
from aiogram.types import Message

from app.keyboards.main_menu import MAIN_MENU

router = Router(name="progress-router")


@router.message(F.text == "📈 Мой прогресс")
async def handle_progress(message: Message):
    # позже здесь будет запрос к CORE (/api/status или спец-эндпоинт)
    await message.answer(
        "📈 Мой прогресс\n\n"
        "Я уже фиксирую события в ядре Элайи.\n"
        "Скоро здесь появится твой реальный прогресс по тренировкам и циклам.",
        reply_markup=MAIN_MENU,
    )
