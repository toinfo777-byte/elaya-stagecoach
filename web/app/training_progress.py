# web/app/training_progress.py
from __future__ import annotations

from datetime import date, timedelta
from typing import Dict, Set, Any


# user_id -> множество дат, в которые была тренировка
_USER_DAYS: Dict[int, Set[date]] = {}


def add_training_day(tg_user_id: int, day: date | None = None) -> None:
    """
    Отметить, что у пользователя была тренировка в указанный день.
    Если day не передан — берём сегодняшнюю дату.
    """
    if day is None:
        day = date.today()

    days = _USER_DAYS.setdefault(tg_user_id, set())
    days.add(day)


def get_progress_summary(tg_user_id: int) -> Dict[str, Any]:
    """
    Вернуть сводку прогресса для пользователя:

        {
            "total_days": int,      # всего уникальных дней с тренировками
            "current_streak": int   # текущая серия по дням (подряд до сегодня)
        }
    """
    days = sorted(_USER_DAYS.get(tg_user_id, set()))
    total = len(days)

    if not days:
        return {"total_days": 0, "current_streak": 0}

    # считаем серию с конца
    streak = 1
    for i in range(len(days) - 2, -1, -1):
        if days[i + 1] - days[i] == timedelta(days=1):
            streak += 1
        else:
            break

    return {
        "total_days": total,
        "current_streak": streak,
    }
