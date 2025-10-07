from __future__ import annotations
import asyncio
import os
from datetime import datetime, timedelta, timezone
import aiosqlite

_DB_PATH = os.getenv("PROGRESS_DB", "progress.sqlite3")

_SCHEMA = """
CREATE TABLE IF NOT EXISTS training_episodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    level TEXT NOT NULL,
    ts_utc INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_training_user_ts ON training_episodes(user_id, ts_utc);
"""

async def _ensure_db():
    async with aiosqlite.connect(_DB_PATH) as db:
        await db.executescript(_SCHEMA)
        await db.commit()

def _utc_now_ts() -> int:
    return int(datetime.now(timezone.utc).timestamp())

async def save_training_episode(user_id: int, level: str) -> None:
    await _ensure_db()
    async with aiosqlite.connect(_DB_PATH) as db:
        await db.execute(
            "INSERT INTO training_episodes(user_id, level, ts_utc) VALUES (?,?,?)",
            (int(user_id), str(level), _utc_now_ts())
        )
        await db.commit()

async def get_progress(user_id: int) -> dict:
    """Возвращает {'streak': int, 'episodes_7d': int}."""
    await _ensure_db()
    now = datetime.now(timezone.utc)
    start_7d = int((now - timedelta(days=7)).timestamp())

    async with aiosqlite.connect(_DB_PATH) as db:
        # эпизоды за 7 дней
        async with db.execute(
            "SELECT ts_utc FROM training_episodes WHERE user_id=? AND ts_utc>=? ORDER BY ts_utc DESC",
            (int(user_id), start_7d)
        ) as cur:
            rows = await cur.fetchall()
            ts_list = [r[0] for r in rows]

    # считаем стрик по датам (день в день по UTC)
    days = { datetime.fromtimestamp(ts, tz=timezone.utc).date() for ts in ts_list }

    streak = 0
    d = now.date()
    while d in days:
        streak += 1
        d = d - timedelta(days=1)

    return {
        "streak": streak,
        "episodes_7d": len(ts_list),
    }
