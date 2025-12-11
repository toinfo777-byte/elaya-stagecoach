# web/app/training_progress.py
from __future__ import annotations

import os
import sqlite3
from datetime import date, datetime
from typing import Dict

DB_PATH = os.getenv("SQLITE_PATH", "data.sqlite3")


def _get_conn() -> sqlite3.Connection:
    """
    Открывает соединение и при необходимости создаёт таблицу.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS training_days (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tg_user_id INTEGER NOT NULL,
            day TEXT NOT NULL,
            created_at TEXT NOT NULL,
            UNIQUE (tg_user_id, day)
        )
        """
    )
    return conn


def add_training_day(tg_user_id: int, day: date) -> None:
    """
    Фиксируем факт тренировки за конкретный день.
    """
    conn = _get_conn()
    try:
        conn.execute(
            """
            INSERT OR IGNORE INTO training_days (tg_user_id, day, created_at)
            VALUES (?, ?, ?)
            """,
            (int(tg_user_id), day.isoformat(), datetime.utcnow().isoformat()),
        )
        conn.commit()
    finally:
        conn.close()


def get_progress_summary(tg_user_id: int) -> Dict[str, int]:
    """
    Возвращает:
      - total_days — всего уникальных дней с тренировкой
      - current_streak — текущая серия по дням, заканчивающаяся сегодня
    """
    conn = _get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT day FROM training_days WHERE tg_user_id = ? ORDER BY day ASC",
            (int(tg_user_id),),
        )
        rows = [date.fromisoformat(row[0]) for row in cur.fetchall()]
    finally:
        conn.close()

    total = len(rows)
    streak = 0

    if rows:
        days_set = set(rows)
        today = date.today()

        # считаем серию, только если в серии есть сегодняшний день
        if today in days_set:
            streak = 1
            d = today
            while True:
                d = date.fromordinal(d.toordinal() - 1)
                if d in days_set:
                    streak += 1
                else:
                    break

    return {"total_days": total, "current_streak": streak}
