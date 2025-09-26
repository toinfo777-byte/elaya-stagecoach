# app/routers/progress.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message

from app.keyboards.reply import main_menu_kb, BTN_PROGRESS
from app.storage.repo_extras import get_progress

router = Router(name="progress")


async def show_progress(target: Message) -> None:
    data = await get_progress(target.from_user.id)
    streak = int(data.get("streak", 0))
    last7 = int(data.get("episodes_7d", 0))
    text = (
        "📈 Мой прогресс\n\n"
        f"• Стрик: {streak}\n"
        f"• Эпизодов за 7 дней: {last7}\n\n"
        "Продолжай каждый день — тренировка дня в один клик 👇"
    )
    await target.answer(text, reply_markup=main_menu_kb())


@router.message(StateFilter("*"), Command("progress"))
async def progress_cmd(m: Message):
    await show_progress(m)


@router.message(StateFilter("*"), F.text == BTN_PROGRESS)
async def progress_btn(m: Message):
    await show_progress(m)


__all__ = ["router", "show_progress"]
