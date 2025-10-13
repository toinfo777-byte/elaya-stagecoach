# app/routers/progress.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message

from app.keyboards.reply import main_menu_kb

router = Router(name="progress")

def _progress_bar(days_done: int, total: int = 7) -> str:
    days_done = max(0, min(days_done, total))
    return "■" * days_done + "□" * (total - days_done)

@router.message(Command("progress"))
@router.message(StateFilter("*"), F.text == "📈 Мой прогресс")
async def show_progress(msg: Message):
    # Заглушка: 1 день из 7 (не падает и не пишет в БД)
    streak = 1
    episodes = 1
    score = 1
    bar = _progress_bar(streak, 7)

    await msg.answer(
        "<b>Мой прогресс</b>\n\n"
        f"• Стрик: {streak}\n"
        f"• Эпизодов за 7 дней: {episodes}\n"
        f"• Очков за 7 дней: {score}\n\n"
        f"{bar}\n\n"
        "Продолжай каждый день — «Тренировка дня» в один клик 🟡",
        reply_markup=main_menu_kb()
    )
