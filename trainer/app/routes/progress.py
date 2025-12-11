# trainer/app/routes/progress.py
from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.types import Message

from app.keyboards.main_menu import MAIN_MENU, BTN_PROGRESS
from app.core_client import fetch_progress

router = Router()
logger = logging.getLogger(__name__)


@router.message(F.text == BTN_PROGRESS)
async def handle_progress(message: Message) -> None:
    """
    Показываем пользователю количество тренировок и текущую серию.
    """
    try:
        data = await fetch_progress(message.from_user.id)
    except Exception as e:
        logger.exception("Progress request failed: %s", e)
        await message.answer(
            "Сейчас я не могу получить данные прогресса.\n"
            "Но тренировка всё равно доступна — жми «🎭 Тренировка дня».",
            reply_markup=MAIN_MENU,
        )
        return

    total = int(data.get("total_days", 0))
    streak = int(data.get("current_streak", 0))

    if total == 0:
        await message.answer(
            "Пока ещё нет сохранённых тренировок.\n"
            "Начни с первой — нажимай «🎭 Тренировка дня».",
            reply_markup=MAIN_MENU,
        )
    else:
        await message.answer(
            (
                "📈 Прогресс\n\n"
                f"• Всего тренировок: <b>{total}</b>\n"
                f"• Текущая серия по дням: <b>{streak}</b>"
            ),
            reply_markup=MAIN_MENU,
        )
