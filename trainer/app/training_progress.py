# trainer/app/training_progress.py
from __future__ import annotations

from datetime import date
from typing import Dict, List, Optional

# Простейшее in-memory хранилище (для отладки тренера без Core/Web)
TRAINING_LOG: List[Dict] = []


def register_training(
    user_id: int,
    date: date,
    vector: str,
    reflect: str,
    transition: str,
    review: str,
) -> None:
    """
    Полная запись дневной тренировки.
    """
    TRAINING_LOG.append(
        {
            "user_id": user_id,
            "date": date.isoformat(),
            "vector": vector,
            "reflect": reflect,
            "transition": transition,
            "review": review,
        }
    )
    print("✔ register_training: saved")


def register_training_simple(user_id: int) -> None:
    """
    Сокращённая запись (используется для UI статистики).
    """
    TRAINING_LOG.append(
        {
            "user_id": user_id,
            "date": date.today().isoformat(),
            "simple": True,
        }
    )
    print("✔ register_training_simple: saved")


def _extract_dates(user_id: Optional[int] = None) -> List[date]:
    """
    Вытаскиваем уникальные даты тренировок (по пользователю, если нужно).
    """
    filtered = (
        [e for e in TRAINING_LOG if e.get("user_id") == user_id]
        if user_id is not None
        else TRAINING_LOG
    )

    if not filtered:
        return []

    unique_dates = {date.fromisoformat(e["date"]) for e in filtered}
    return sorted(unique_dates)


def _calc_streak(dates: List[date]) -> int:
    """
    Считаем текущую серию по календарю:
    последний день + подряд назад по -1 день.
    """
    if not dates:
        return 0

    # Начинаем с последней даты и идём назад
    streak = 1
    last = dates[-1]

    for i in range(len(dates) - 2, -1, -1):
        if (last - dates[i]).days == 1:
            streak += 1
            last = dates[i]
        else:
            break

    return streak


def get_progress_summary(
    user_id: Optional[int] = None,
    limit: Optional[int] = None,
) -> Dict[str, object]:
    """
    Простейший отчёт для кнопки «Мой прогресс».

    Возвращаем формат, который ожидает тренер:

        {
            "total_days": int,
            "current_streak": int,
            "last_date": "YYYY-MM-DD" | None,
        }
    """
    dates = _extract_dates(user_id=user_id)

    if not dates:
        return {
            "total_days": 0,
            "current_streak": 0,
            "last_date": None,
        }

    if limit is not None and limit > 0:
        dates = dates[-limit:]

    total_days = len(dates)
    current_streak = _calc_streak(dates)
    last_date = dates[-1].isoformat() if dates else None

    return {
        "total_days": total_days,
        "current_streak": current_streak,
        "last_date": last_date,
    }
