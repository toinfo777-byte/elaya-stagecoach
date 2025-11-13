import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Optional

DB_PATH = Path("data.db")


class TimelineStore:
    """Персистентное хранилище событий Элайи (SQLite, auto-init)."""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _conn(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._conn() as c:
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS events(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT NOT NULL,
                    text   TEXT,
                    created_at TEXT NOT NULL
                );
                """
            )
            c.commit()

    def add_event(self, source: str, text: str) -> None:
        ts = datetime.now(timezone.utc).isoformat()
        with self._conn() as c:
            c.execute(
                "INSERT INTO events(source,text,created_at) VALUES (?,?,?)",
                (source, text, ts),
            )
            c.commit()

    def get_events(self, limit: int = 200, source: Optional[str] = None) -> List[Dict]:
        with self._conn() as c:
            if source:
                rows = c.execute(
                    "SELECT id,source,text,created_at "
                    "FROM events WHERE source=? ORDER BY id DESC LIMIT ?",
                    (source, limit),
                ).fetchall()
            else:
                rows = c.execute(
                    "SELECT id,source,text,created_at "
                    "FROM events ORDER BY id DESC LIMIT ?",
                    (limit,),
                ).fetchall()
        return [
            {"id": r[0], "source": r[1], "text": r[2], "created_at": r[3]} for r in rows
        ]

    def purge(self) -> None:
        with self._conn() as c:
            c.execute("DELETE FROM events")
            c.commit()
