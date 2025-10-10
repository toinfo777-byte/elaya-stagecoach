from __future__ import annotations

import os
import sqlite3
import time
import logging
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import List, Tuple, Optional

log = logging.getLogger(__name__)

_DB_PATH_ENV = os.getenv("PROGRESS_DB_PATH")  # можно указать в ENV
_DB_PATH = _DB_PATH_ENV or os.getenv("DATABASE_FILE") or "/data/elaya_progress.sqlite3"

# ──────────────────────────────────────────────────────────────────────────────
# Общая инициализация
# ──────────────────────────────────────────────────────────────────────────────
def _connect() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(_DB_PATH), exist_ok=True)
    conn = sqlite3.connect(_DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_schema() -> None:
    """
    Вызывается при старте из app/main.py.
    Делает БД для прогресса (idempotent).
    """
    conn = _connect()
    try:
        # Таблица эпизодов прогресса
        conn.execute("""
        CREATE TABLE IF NOT EXISTS episodes (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id   INTEGER NOT NULL,
            kind      TEXT    NOT NULL,      -- "training" / "casting" / etc
            points    INTEGER NOT NULL DEFAULT 1,
            ts        INTEGER NOT NULL       -- unix epoch (UTC)
        );
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_ep_user_ts ON episodes(user_id, ts);")
        conn.commit()
    finally:
        conn.close()


# ──────────────────────────────────────────────────────────────────────────────
# Прогресс
# ──────────────────────────────────────────────────────────────────────────────
@dataclass
class ProgressSummary:
    streak: int
    episodes_7d: int
    points_7d: int
    last_days: List[Tuple[str, int]]  # [(YYYY-MM-DD, episodes_count)]


class ProgressRepo:
    """
    Лёгкий репозиторий прогресса на SQLite (UTC-даты).
    """
    def __init__(self, db_path: Optional[str] = None) -> None:
        self.db_path = db_path or _DB_PATH

    # low-level
    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    # API
    async def add_episode(self, *, user_id: int, kind: str = "training", points: int = 1) -> None:
        """
        Фиксируем завершение шага/тренировки.
        """
        ts = int(time.time())
        conn = self._conn()
        try:
            conn.execute(
                "INSERT INTO episodes(user_id, kind, points, ts) VALUES (?, ?, ?, ?)",
                (user_id, kind, points, ts),
            )
            conn.commit()
        finally:
            conn.close()

    async def get_summary(self, *, user_id: int) -> ProgressSummary:
        """
        Стрик (по дням, UTC) + агрегации за последние 7 дней.
        """
        conn = self._conn()
        try:
            now = datetime.now(timezone.utc)
            start_7 = int((now - timedelta(days=7)).timestamp())
            rows = conn.execute(
                "SELECT ts, points FROM episodes WHERE user_id=? AND ts>=? ORDER BY ts DESC",
                (user_id, start_7),
            ).fetchall()

            # группируем по дню
            per_day: dict[str, int] = {}
            for r in rows:
                d = datetime.fromtimestamp(r["ts"], tz=timezone.utc).date().isoformat()
                per_day[d] = per_day.get(d, 0) + 1

            # последние 7 дней
            days_list: List[Tuple[str, int]] = []
            for i in range(7):
                d = (now.date() - timedelta(days=6 - i)).isoformat()
                days_list.append((d, per_day.get(d, 0)))

            # стрик: сколько подряд дней до сегодня включительно есть эпизоды
            streak = 0
            cur = now.date()
            while per_day.get(cur.isoformat(), 0) > 0:
                streak += 1
                cur = cur - timedelta(days=1)

            # очки/эпизоды за 7 дней
            points_7d = sum(int(r["points"]) for r in rows)
            episodes_7d = sum(cnt for _, cnt in days_list)

            return ProgressSummary(
                streak=streak,
                episodes_7d=episodes_7d,
                points_7d=points_7d,
                last_days=days_list,
            )
        finally:
            conn.close()


# Синглтон
progress = ProgressRepo()


# ──────────────────────────────────────────────────────────────────────────────
# Заглушка под кастинг — АСИНХРОННАЯ (важно, т.к. вызывается через await)
# ──────────────────────────────────────────────────────────────────────────────
async def save_casting(
    *,
    tg_id: int,
    name: str,
    age: int,
    city: str,
    experience: str,
    contact: str,
    portfolio: Optional[str],
    agree_contact: bool = True,
) -> None:
    """
    Пока просто логируем. В будущем можно писать в отдельную таблицу.
    """
    log.info(
        "save_casting(tg_id=%s): name=%r, age=%s, city=%r, exp=%r, contact=%r, portfolio=%r, agree=%s",
        tg_id, name, age, city, experience, contact, portfolio, agree_contact,
    )
