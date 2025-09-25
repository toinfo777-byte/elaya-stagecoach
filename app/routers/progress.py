from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message
from app.keyboards.reply import main_menu_kb, BTN_PROGRESS

router = Router(name="progress")

@router.message(StateFilter("*"), Command("progress"))
@router.message(StateFilter("*"), F.text == BTN_PROGRESS)
async def show_progress(m: Message):
    await m.answer(
        "📈 Мой прогресс\n\n• Стрик: 0\n• Этюдов за 7 дней: 0\n\n"
        "Продолжай каждый день — тренировка дня в один клик 👇",
        reply_markup=main_menu_kb()
    )
