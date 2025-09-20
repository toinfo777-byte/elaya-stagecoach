# app/bot/routers/progress.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from app.bot.keyboards.menu import main_menu, BTN_PROGRESS

router = Router(name="progress")

# Псевдо-данные прогресса (потом можно заменить на БД)
_USER_PROGRESS: dict[int, dict[str, int]] = {}


def _get_progress(user_id: int) -> dict[str, int]:
    if user_id not in _USER_PROGRESS:
        _USER_PROGRESS[user_id] = {"streak": 0, "etudes": 0}
    return _USER_PROGRESS[user_id]


@router.message(Command("progress"))
@router.message(F.text == BTN_PROGRESS)
async def progress_entry(message: Message) -> None:
    """Раздел '📈 Мой прогресс'"""
    data = _get_progress(message.from_user.id)

    streak = data["streak"]
    etudes = data["etudes"]

    text = (
        f"📈 <b>Мой прогресс</b>\n\n"
        f"• Стрик: {streak}\n"
        f"• Этюдов за 7 дней: {etudes}\n\n"
        "Продолжай каждый день — тренировка дня в один клик 👇"
    )

    await message.answer(text, reply_markup=main_menu(), parse_mode="HTML")
