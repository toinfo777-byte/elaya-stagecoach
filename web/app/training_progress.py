# web/app/training_progress.py
from __future__ import annotations

from datetime import date, timedelta
from typing import Dict, Set

# Минимальный прогресс: in-memory по tg_user_id.
# Для локальной отладки достаточно. Позже заменим на SQLite/Postgres.

_USER_DAYS: Dict[int, Set[date]] = {}


def add_training_day(tg_user_id: int, day: date) -> None:
    days = _USER_DAYS.setdefault(int(tg_user_id), set())
    days.add(day)


def get_progress_summary(tg_user_id: int) -> Dict[str, int]:
    days = sorted(_USER_DAYS.get(int(tg_user_id), set()))
    if not days:
        return {"total_days": 0, "current_streak": 0}

    total_days = len(days)

    # streak считаем от последнего дня назад по 1 дню
    streak = 1
    for i in range(len(days) - 1, 0, -1):
        if days[i] - days[i - 1] == timedelta(days=1):
            streak += 1
        else:
            break

    return {"total_days": total_days, "current_streak": streak}
