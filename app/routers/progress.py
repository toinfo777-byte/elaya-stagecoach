# app/routers/progress.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from app.keyboards.menu import main_menu, BTN_PROGRESS

router = Router(name="progress")


@router.message(F.text == BTN_PROGRESS)
@router.message(Command("progress"))
async def progress_entry(m: Message) -> None:
    await m.answer("📈 Мой прогресс\n\n• Стрик: 0\n• Этюдов за 7 дней: 0", reply_markup=main_menu())
