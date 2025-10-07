from __future__ import annotations
import os
from pathlib import Path
from datetime import datetime, timedelta, timezone
import aiosqlite
import logging

log = logging.getLogger("repo_extras")

# ── путь к БД ──────────────────────────────────────────────────────
# На Render ПОДКЛЮЧИ persistent disk и выставь PROGRESS_DB=/data/progress.sqlite3
# Локально можно оставить progress.sqlite3 в корне проекта.
_DB_PATH = os.getenv("PROGRESS_DB", "progress.sqlite3")

def _ensure_dir(path: str) -> None:
    p = Path(path).expanduser().resolve()
    if p.parent.exists():
        return
    p.parent.mkdir(parents=True, exist_ok=True)

_SCHEMA = """
CREATE TABLE IF NOT EXISTS training_episodes (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id  INTEGER NOT NULL,
    level    TEXT    NOT NULL,
    ts_utc   INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_training_user_ts
    ON training_episodes(user_id, ts_utc);
"""

async def _open() -> aiosqlite.Connection:
    _ensure_dir(_DB_PATH)
    db = await aiosqlite.connect(_DB_PATH)
    await db.execute("PRAGMA journal_mode=WAL;")
    await db.execute("PRAGMA synchronous=NORMAL;")
    return db

async def _ensure_db() -> None:
    async with await _open() as db:
        await db.executescript(_SCHEMA)
        await db.commit()
    log.info("DB ready at %s", _DB_PATH)

def _utc_now_ts() -> int:
    return int(datetime.now(timezone.utc).timestamp())

# ── публичные функции ─────────────────────────────────────────────
async def save_training_episode(user_id: int, level: str) -> None:
    """Сохраняем факт выполнения тренировки."""
    await _ensure_db()
    try:
        async with await _open() as db:
            await db.execute(
                "INSERT INTO training_episodes(user_id, level, ts_utc) VALUES (?,?,?)",
                (int(user_id), str(level), _utc_now_ts())
            )
            await db.commit()
        log.info("episode saved: uid=%s level=%s", user_id, level)
    except Exception:
        log.exception("failed to save episode (uid=%s, level=%s)", user_id, level)
        raise

async def get_progress(user_id: int) -> dict:
    """Возвращает {'streak': int, 'episodes_7d': int}."""
    await _ensure_db()
    now = datetime.now(timezone.utc)
    start_7d = int((now - timedelta(days=7)).timestamp())

    try:
        async with await _open() as db:
            async with db.execute(
                "SELECT ts_utc FROM training_episodes "
                "WHERE user_id=? AND ts_utc>=? ORDER BY ts_utc DESC",
                (int(user_id), start_7d)
            ) as cur:
                rows = await cur.fetchall()
                ts_list = [r[0] for r in rows]
    except Exception:
        log.exception("failed to read progress (uid=%s)", user_id)
        raise

    days = { datetime.fromtimestamp(ts, tz=timezone.utc).date() for ts in ts_list }

    streak = 0
    d = now.date()
    while d in days:
        streak += 1
        d = d - timedelta(days=1)

    res = {"streak": streak, "episodes_7d": len(ts_list)}
    log.info("progress: uid=%s %s", user_id, res)
    return res
