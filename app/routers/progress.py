# app/routers/progress.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery

from app.keyboards.reply import main_menu_kb, BTN_PROGRESS
from app.storage.repo_extras import get_progress

router = Router(name="progress")

def _format_progress(streak: int, last7: int, updated_at_str: str) -> str:
    return (
        "📈 Мой прогресс\n\n"
        f"• Стрик: {streak}\n"
        f"• Этюдов за 7 дней: {last7}\n\n"
        f"Обновлено: {updated_at_str}\n"
        "Продолжай каждый день — «Тренировка дня» в один клик 👇"
    )

@router.message(StateFilter("*"), Command("progress"))
@router.message(StateFilter("*"), F.text == BTN_PROGRESS)
async def show_progress_cmd(msg: Message):
    streak, last7, updated_at = await get_progress(msg.from_user.id)
    ts = updated_at.strftime("%Y-%m-%d %H:%M UTC")
    await msg.answer(_format_progress(streak, last7, ts), reply_markup=main_menu_kb())

@router.callback_query(StateFilter("*"), F.data == "go:progress")
async def show_progress_cb(cb: CallbackQuery):
    streak, last7, updated_at = await get_progress(cb.from_user.id)
    ts = updated_at.strftime("%Y-%m-%d %H:%M UTC")
    await cb.message.answer(_format_progress(streak, last7, ts), reply_markup=main_menu_kb())
    await cb.answer()
