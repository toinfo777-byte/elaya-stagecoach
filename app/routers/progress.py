# app/routers/progress.py
from __future__ import annotations
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from app.keyboards.reply import main_menu_kb, BTN_PROGRESS
from app.storage.repo import progress  # наш синглтон из repo.py

router = Router(name="progress")

@router.message(Command("progress"))
@router.message(F.text == BTN_PROGRESS)
async def show_progress(m: Message):
    try:
        summary = await progress.get_summary(user_id=m.from_user.id)
        days = "\n".join(f"• {d}: {cnt}" for d, cnt in summary.last_days)
        await m.answer(
            "📈 Прогресс (демо)\n"
            f"Streak: {summary.streak}\n"
            f"Episodes(7d): {summary.episodes_7d}\n"
            f"Points(7d): {summary.points_7d}\n\n"
            f"Последние 7 дней:\n{days}",
            reply_markup=main_menu_kb()
        )
    except Exception:
        await m.answer("📈 Прогресс: пока пусто. Сделай первое упражнение!", reply_markup=main_menu_kb())
