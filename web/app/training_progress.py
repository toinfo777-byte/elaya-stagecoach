# web/app/training_progress.py
from __future__ import annotations

import logging
import os
import sqlite3
from datetime import date, timedelta
from typing import Dict

logger = logging.getLogger(__name__)

# Путь к SQLite-файлу берём из переменной окружения
DB_PATH = os.getenv("SQLITE_PATH", "data.sqlite3")


def _get_conn() -> sqlite3.Connection:
    """
    Открываем соединение и гарантируем наличие таблицы.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS training_days (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tg_user_id INTEGER NOT NULL,
            day TEXT NOT NULL,
            UNIQUE (tg_user_id, day)
        )
        """
    )
    return conn


def add_training_day(tg_user_id: int, when: date | None = None) -> None:
    """
    Фиксируем тренировочный день для пользователя.
    Если when не передан — берём сегодняшнюю дату.
    """
    if when is None:
        when = date.today()

    day_str = when.isoformat()
    conn: sqlite3.Connection | None = None

    try:
        conn = _get_conn()
        with conn:
            conn.execute(
                "INSERT OR IGNORE INTO training_days (tg_user_id, day) VALUES (?, ?)",
                (tg_user_id, day_str),
            )
    except Exception:
        logger.exception(
            "Failed to add_training_day: user=%s day=%s", tg_user_id, day_str
        )
    finally:
        if conn is not None:
            conn.close()


def get_progress_summary(
    tg_user_id: int,
    limit: int = 60,
) -> Dict[str, int]:
    """
    Возвращает сводку прогресса по пользователю.

    total_days      — сколько уникальных дней с тренировками вообще.
    current_streak  — текущая серия подряд идущих дней.
    """
    today = date.today()
    conn: sqlite3.Connection | None = None

    try:
        conn = _get_conn()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT day
            FROM training_days
            WHERE tg_user_id = ?
              AND day <= ?
            ORDER BY day DESC
            """,
            (tg_user_id, today.isoformat()),
        )
        rows = cur.fetchall()
    except Exception:
        logger.exception("Failed to get_progress_summary for user=%s", tg_user_id)
        return {"total_days": 0, "current_streak": 0}
    finally:
        if conn is not None:
            conn.close()

    # Преобразуем строки в date
    days = [date.fromisoformat(r[0]) for r in rows]
    total = len(days)

    if not days:
        return {"total_days": 0, "current_streak": 0}

    day_set = set(days)

    # Пытаемся считать серию от сегодняшнего дня.
    streak = 0
    for i in range(limit):
        d = today - timedelta(days=i)
        if d in day_set:
            streak += 1
        else:
            # Если за сегодня записи нет — серия может начинаться
            # с последнего тренировочного дня.
            if i == 0:
                base = days[0]  # самая поздняя дата
                streak = 0
                for j in range(limit):
                    d2 = base - timedelta(days=j)
                    if d2 in day_set:
                        streak += 1
                    else:
                        break
            break

    return {"total_days": total, "current_streak": streak}
