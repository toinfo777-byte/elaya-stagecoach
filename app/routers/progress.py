from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.storage.repo import progress  # синглтон ProgressRepo

router = Router(name="progress")


def _days_bar(last_days: list[tuple[str, int]]) -> str:
    """
    Рисуем простую полоску за 7 дней: ◻︎/■
    """
    cells = []
    for _, cnt in last_days:
        cells.append("■" if cnt > 0 else "◻︎")
    return "".join(cells)


async def show_progress(m: Message):
    s = await progress.get_summary(user_id=m.from_user.id)
    bar = _days_bar(s.last_days)
    text = (
        "<b>Мой прогресс</b>\n\n"
        f"• Стрик: <b>{s.streak}</b>\n"
        f"• Эпизодов за 7 дней: <b>{s.episodes_7d}</b>\n"
        f"• Очков за 7 дней: <b>{s.points_7d}</b>\n\n"
        f"{bar}\n"
        "Продолжай каждый день — «Тренировка дня» в один клик 🟡"
    )
    await m.answer(text)


# Команда на всякий случай
@router.message(Command("progress"))
async def cmd_progress(m: Message):
    await show_progress(m)


# Утилита: можно вызывать из тренировки
async def record_training_episode(m: Message, points: int = 1):
    await progress.add_episode(user_id=m.from_user.id, kind="training", points=points)
