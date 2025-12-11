# web/app/training_progress.py
from __future__ import annotations

import logging
import os
import sqlite3
from datetime import date, timedelta

logger = logging.getLogger(__name__)

# Путь к базе — как в .env (ENV=prod, MODE=web)
DB_PATH = os.getenv("SQLITE_PATH", "data.sqlite3")


def _get_conn() -> sqlite3.Connection:
    """
    Открываем соединение к SQLite.
    Отдельное соединение на каждый вызов — безопасно и просто.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _init_db() -> None:
    """
    Создаём таблицу для тренировочных дней, если её ещё нет.
    """
    with _get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS training_days (
                tg_user_id INTEGER NOT NULL,
                day        TEXT    NOT NULL,
                PRIMARY KEY (tg_user_id, day)
            )
            """
        )
        conn.commit()


# Инициализация при старте ядра
_init_db()


def add_training_day(tg_user_id: int, day: date | None = None) -> None:
    """
    Записываем день тренировки для пользователя (id + дата).
    Если запись за этот день уже есть — тихо игнорируем.
    """
    if day is None:
        day = date.today()

    day_str = day.isoformat()

    try:
        with _get_conn() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO training_days (tg_user_id, day) VALUES (?, ?)",
                (int(tg_user_id), day_str),
            )
            conn.commit()

        logger.info("training day recorded: tg_user_id=%s day=%s", tg_user_id, day_str)
    except Exception:
        # Не роняем ядро, просто логируем
        logger.exception(
            "failed to add_training_day tg_user_id=%s day=%s",
            tg_user_id,
            day_str,
        )


def _load_user_days(tg_user_id: int) -> list[date]:
    """
    Все дни тренировок пользователя, отсортированные по возрастанию.
    """
    with _get_conn() as conn:
        cur = conn.execute(
            "SELECT day FROM training_days WHERE tg_user_id = ? ORDER BY day ASC",
            (int(tg_user_id),),
        )
        rows = cur.fetchall()

    return [date.fromisoformat(row["day"]) for row in rows]


def get_progress_summary(tg_user_id: int) -> dict[str, int]:
    """
    Возвращает словарь:
      {
        "total_days": int,       # сколько разных дней есть в базе
        "current_streak": int    # длина последней непрерывной серии по дням
      }

    Серия считается так:
    - Берём все даты пользователя
    - Считаем длину последней последовательности,
      где каждая следующая дата = предыдущая + 1 день.
    """
    try:
        days = _load_user_days(tg_user_id)
    except Exception:
        logger.exception("failed to load progress for tg_user_id=%s", tg_user_id)
        # В случае ошибки не валим /api/progress, а отдаём нули
        return {"total_days": 0, "current_streak": 0}

    total = len(days)
    if total == 0:
        return {"total_days": 0, "current_streak": 0}

    # Серия с конца: последняя дата всегда входит в серию
    streak = 1
    # пары (предыдущий, текущий) в обратном порядке
    for prev, curr in zip(reversed(days[:-1]), reversed(days[1:])):
        if (curr - prev) == timedelta(days=1):
            streak += 1
        else:
            break

    return {"total_days": total, "current_streak": streak}
