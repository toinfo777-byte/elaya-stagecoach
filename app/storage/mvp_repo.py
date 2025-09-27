from __future__ import annotations
from datetime import date, datetime, timedelta
from typing import Dict, Any

from sqlalchemy import create_engine, text
from app.config import settings

_engine = create_engine(settings.db_url, future=True)


def init_schema() -> None:
    """Создаём минимальные таблицы под MVP (idempotent)."""
    with _engine.begin() as conn:
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS training_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            day DATE NOT NULL,
            level TEXT NOT NULL,
            done INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (user_id, day)
        );
        """))
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS casting_applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            payload TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """))


def log_training(user_id: int, level: str, done: bool, day: date | None = None) -> None:
    """Upsert запись тренировки на день."""
    d = day or date.today()
    with _engine.begin() as conn:
        conn.execute(text("DELETE FROM training_log WHERE user_id=:uid AND day=:d"),
                     {"uid": user_id, "d": d})
        conn.execute(text("""
            INSERT INTO training_log(user_id, day, level, done, created_at)
            VALUES(:uid, :d, :level, :done, :ts)
        """), {"uid": user_id, "d": d, "level": level, "done": 1 if done else 0, "ts": datetime.utcnow()})


def progress_for(user_id: int) -> tuple[int, int]:
    """Возвращает (streak, count_7_days)."""
    today = date.today()
    week_ago = today - timedelta(days=6)
    with _engine.begin() as conn:
        rows = conn.execute(text("""
            SELECT day, done FROM training_log
            WHERE user_id=:uid AND done=1
            ORDER BY day DESC
        """), {"uid": user_id}).all()
        last7 = conn.execute(text("""
            SELECT COUNT(*) FROM training_log
            WHERE user_id=:uid AND done=1 AND day>=:d
        """), {"uid": user_id, "d": week_ago}).scalar_one()

    # считаем стрик от сегодня назад
    streak = 0
    days = {r[0] for r in rows}
    cursor = today
    while cursor in days:
        streak += 1
        cursor -= timedelta(days=1)
    return streak, int(last7 or 0)


def save_casting_application(user_id: int, payload_json: str) -> int:
    with _engine.begin() as conn:
        res = conn.execute(text("""
            INSERT INTO casting_applications(user_id, payload)
            VALUES(:uid, :payload)
        """), {"uid": user_id, "payload": payload_json})
        # sqlite возвращает lastrowid
        return int(res.lastrowid or 0)


def purge_user(user_id: int) -> None:
    with _engine.begin() as conn:
        conn.execute(text("DELETE FROM training_log WHERE user_id=:uid"), {"uid": user_id})
        conn.execute(text("DELETE FROM casting_applications WHERE user_id=:uid"), {"uid": user_id})
