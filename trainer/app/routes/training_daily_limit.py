# trainer/app/routes/training_daily_limit.py
from __future__ import annotations

from datetime import date
from typing import Dict

# Простое in-memory хранилище: user_id -> дата последней завершённой тренировки
_LAST_TRAINING_DATE: Dict[int, date] = {}


def is_training_allowed(user_id: int) -> bool:
    """
    Можно ли запускать тренировку для этого пользователя сегодня.

    True  — тренировка ещё не делалась сегодня
    False — тренировка уже завершена (по нашему учёту)
    """
    last = _LAST_TRAINING_DATE.get(user_id)
    if last is None:
        return True
    return last != date.today()


def mark_training_done(user_id: int) -> None:
    """
    Отметить, что пользователь завершил тренировку сегодня.
    Вызываем в конце тренировки.
    """
    _LAST_TRAINING_DATE[user_id] = date.today()
