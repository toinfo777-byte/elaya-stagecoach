# app/routers/progress.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message

from app.keyboards.menu import main_menu
from app.storage.repo import calc_progress

try:
    from app.keyboards.menu import BTN_PROGRESS  # type: ignore
except Exception:
    BTN_PROGRESS = "📈 Мой прогресс"

router = Router(name="progress")

@router.message(Command("progress"), StateFilter(None))
@router.message(F.text == BTN_PROGRESS, StateFilter(None))
async def show_progress(m: Message) -> None:
    streak, last7 = await calc_progress(m.from_user.id)
    await m.answer(
        "<b>Мой прогресс</b>\n"
        f"• Стрик: {streak}\n"
        f"• Эпизодов за 7 дней: {last7}\n\n"
        "Продолжай каждый день — «Тренировка дня» в один клик 👇",
        reply_markup=main_menu()
    )
