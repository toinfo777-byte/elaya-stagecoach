# app/routers/progress.py
from __future__ import annotations
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router(name="progress")

@router.message(Command("progress"))
async def show_progress(m: Message):
    await m.answer(
        "📈 Мой прогресс\n\n"
        "Пока раздел находится в разработке.\n"
        "Здесь позже появится статистика твоих тренировок."
    )

__all__ = ["router", "show_progress"]
