import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path("data/memory.db")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with _connect() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS stats (
            id INTEGER PRIMARY KEY,
            intro INTEGER DEFAULT 0,
            reflect INTEGER DEFAULT 0,
            transition INTEGER DEFAULT 0,
            last_updated TEXT
        )
        """)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS reflections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            created_at TEXT
        )
        """)
        # ensure one stats row exists
        conn.execute("INSERT OR IGNORE INTO stats (id) VALUES (1)")
        conn.commit()

def get_stats() -> dict:
    with _connect() as conn:
        row = conn.execute("SELECT * FROM stats WHERE id=1").fetchone()
        if not row:
            return {"intro": 0, "reflect": 0, "transition": 0, "last_updated": ""}
        return dict(row)

def update_stats(field: str):
    if field not in ("intro", "reflect", "transition"):
        return
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with _connect() as conn:
        conn.execute(f"UPDATE stats SET {field} = {field} + 1, last_updated=? WHERE id=1", (now,))
        conn.commit()

def save_reflection(text: str):
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with _connect() as conn:
        conn.execute("INSERT INTO reflections (text, created_at) VALUES (?, ?)", (text, now))
        conn.commit()

def last_reflection() -> dict:
    with _connect() as conn:
        row = conn.execute("SELECT text, created_at FROM reflections ORDER BY id DESC LIMIT 1").fetchone()
        return dict(row) if row else {"text": "", "created_at": ""}
