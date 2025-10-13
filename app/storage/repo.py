# app/storage/repo.py
from __future__ import annotations

import os
import sqlite3
import time
import logging
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import List, Tuple, Optional, Dict, Any

log = logging.getLogger(__name__)

_DB_PATH = os.getenv("PROGRESS_DB_PATH") or os.getenv("DATABASE_FILE") or "/data/elaya_progress.sqlite3"


# ──────────────────────────────────────────────────────────────────────────────
# low-level
# ──────────────────────────────────────────────────────────────────────────────
def _connect() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(_DB_PATH), exist_ok=True)
    conn = sqlite3.connect(_DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_schema() -> None:
    """
    Создаёт/мигрит простые таблицы. Идём без внешних зависимостей.
    """
    conn = _connect()
    try:
        # Прогресс (эпизоды)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS episodes (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id   INTEGER NOT NULL,
            kind      TEXT    NOT NULL,    -- "training" / "casting" / etc
            points    INTEGER NOT NULL DEFAULT 1,
            ts        INTEGER NOT NULL     -- unix epoch (UTC)
        );
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_ep_user_ts ON episodes(user_id, ts);")

        # Заявки кастинга (длинная форма)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS casting_applications (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            tg_id     INTEGER NOT NULL,
            name      TEXT,
            age       INTEGER,
            city      TEXT,
            experience TEXT,
            contact   TEXT,
            portfolio TEXT,
            agree_contact INTEGER NOT NULL DEFAULT 1,
            ts        INTEGER NOT NULL
        );
        """)

        # Сессии мини-кастинга (очень простая структура)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS casting_sessions (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            tg_id     INTEGER NOT NULL,
            payload   TEXT,                 -- json/text с ответами/шагами
            ts        INTEGER NOT NULL
        );
        """)

        # Отзывы/фидбек (мини-кастинг и др.)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            tg_id     INTEGER NOT NULL,
            rating    INTEGER,
            text      TEXT,
            ts        INTEGER NOT NULL
        );
        """)

        conn.commit()
    finally:
        conn.close()


# ──────────────────────────────────────────────────────────────────────────────
# Примитивная модель прогресса (для /progress и т.п.)
# ──────────────────────────────────────────────────────────────────────────────
@dataclass
class ProgressSummary:
    streak: int
    episodes_7d: int
    points_7d: int
    last_days: List[Tuple[str, int]]  # [(YYYY-MM-DD, episodes_count)]


class ProgressRepo:
    def __init__(self, db_path: Optional[str] = None) -> None:
        self.db_path = db_path or _DB_PATH

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    async def add_episode(self, *, user_id: int, kind: str = "training", points: int = 1) -> None:
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
        conn = self._conn()
        try:
            now = datetime.now(timezone.utc)
            start_7 = int((now - timedelta(days=7)).timestamp())
            rows = conn.execute(
                "SELECT ts, points FROM episodes WHERE user_id=? AND ts>=? ORDER BY ts DESC",
                (user_id, start_7),
            ).fetchall()

            per_day: Dict[str, int] = {}
            for r in rows:
                d = datetime.fromtimestamp(r["ts"], tz=timezone.utc).date().isoformat()
                per_day[d] = per_day.get(d, 0) + 1

            days_list: List[Tuple[str, int]] = []
            for i in range(7):
                d = (now.date() - timedelta(days=6 - i)).isoformat()
                days_list.append((d, per_day.get(d, 0)))

            streak = 0
            cur = now.date()
            while per_day.get(cur.isoformat(), 0) > 0:
                streak += 1
                cur = cur - timedelta(days=1)

            points_7d = sum(int(r["points"]) for r in rows)
            episodes_7d = sum(cnt for _, cnt in days_list)
            return ProgressSummary(streak, episodes_7d, points_7d, days_list)
        finally:
            conn.close()


progress = ProgressRepo()


# ──────────────────────────────────────────────────────────────────────────────
# Контракт для кастинга/мини-кастинга (async, чтобы можно было `await`-ить)
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
    ts = int(time.time())
    conn = _connect()
    try:
        conn.execute(
            """INSERT INTO casting_applications
               (tg_id, name, age, city, experience, contact, portfolio, agree_contact, ts)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (tg_id, name, age, city, experience, contact, portfolio, 1 if agree_contact else 0, ts),
        )
        conn.commit()
        log.info("save_casting: tg_id=%s, name=%r, age=%s, city=%r", tg_id, name, age, city)
    finally:
        conn.close()


async def save_casting_session(*, tg_id: int, payload: str) -> None:
    """
    Мини-кастинг — сохранить «шаги/ответы» одним куском текста/JSON.
    """
    ts = int(time.time())
    conn = _connect()
    try:
        conn.execute(
            "INSERT INTO casting_sessions(tg_id, payload, ts) VALUES (?, ?, ?)",
            (tg_id, payload, ts),
        )
        conn.commit()
        log.info("save_casting_session: tg_id=%s", tg_id)
    finally:
        conn.close()


async def save_feedback(*, tg_id: int, text: str, rating: Optional[int] = None) -> None:
    ts = int(time.time())
    conn = _connect()
    try:
        conn.execute(
            "INSERT INTO feedback(tg_id, rating, text, ts) VALUES (?, ?, ?, ?)",
            (tg_id, rating, text, ts),
        )
        conn.commit()
        log.info("save_feedback: tg_id=%s, rating=%s", tg_id, rating)
    finally:
        conn.close()


async def log_progress_event(*, tg_id: int, kind: str, points: int = 1) -> None:
    # тупо прокидываем в episodes как «событие прогресса»
    await progress.add_episode(user_id=tg_id, kind=kind, points=points)
