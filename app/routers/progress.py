from __future__ import annotations
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

progress_router = Router(name="progress")

def _bar(streak: int, width: int = 7) -> str:
    streak = max(0, min(width, streak))
    return "🟩" * streak + "⬜" * (width - streak)

@progress_router.message(Command("progress"))
@progress_router.message(F.text.casefold().in_({"📈 мой прогресс", "мой прогресс", "progress"}))
async def show_progress(m: Message):
    # Пока простая «рабочая» заглушка: стрик 1
    streak = 1
    await m.answer(
        "📈 <b>Мой прогресс</b>\n"
        f"• Стрик: {streak}\n"
        f"• Эпизодов за 7 дней: {streak}\n"
        f"• Очков за 7 дней: {streak}\n\n"
        f"{_bar(streak)}\n"
        "Продолжай каждый день — «Тренировка дня» в один клик. ✨"
    )
