import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Optional


DB_PATH = Path("data.db")


class TimelineStore:
    """Персистентное хранилище событий ядра Элайи."""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        """Создаёт таблицу, если отсутствует."""
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT NOT NULL,
                    text TEXT,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def add_event(self, source: str, text: str):
        """Добавляет новое событие в хранилище."""
        ts = datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO events (source, text, created_at) VALUES (?, ?, ?)",
                (source, text, ts),
            )
            conn.commit()

    def get_events(self, limit: int = 100, source: Optional[str] = None) -> List[Dict]:
        """Возвращает события (опционально фильтр по source)."""
        with self._connect() as conn:
            cur = conn.cursor()
            if source:
                cur.execute(
                    "SELECT id, source, text, created_at FROM events WHERE source=? ORDER BY id DESC LIMIT ?",
                    (source, limit),
                )
            else:
                cur.execute(
                    "SELECT id, source, text, created_at FROM events ORDER BY id DESC LIMIT ?",
                    (limit,),
                )
            rows = cur.fetchall()
        return [
            {"id": r[0], "source": r[1], "text": r[2], "created_at": r[3]} for r in rows
        ]

    def purge(self):
        """Полная очистка событий."""
        with self._connect() as conn:
            conn.execute("DELETE FROM events")
            conn.commit()
