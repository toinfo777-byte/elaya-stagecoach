from __future__ import annotations

from datetime import date
from typing import Dict

# Простая in-memory таблица:
# user_id -> дата последней тренировки
_last_training_by_user: Dict[int, date] = {}


def is_training_done_today(user_id: int) -> bool:
    """
    Проверяет, проходил ли пользователь тренировку сегодня.
    """
    today = date.today()
    return _last_training_by_user.get(user_id) == today


def mark_training_started(user_id: int) -> None:
    """
    Помечает, что пользователь начал тренировку сегодня.
    """
    _last_training_by_user[user_id] = date.today()
