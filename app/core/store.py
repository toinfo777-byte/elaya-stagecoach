from __future__ import annotations
import os, sqlite3, threading
from dataclasses import dataclass
from datetime import datetime

DB_URL = os.getenv("DB_URL", "sqlite:////data/elaya.db")
_lock = threading.RLock()

def _db_path_from_url(url: str) -> str:
    if not url.startswith("sqlite:"):
        raise RuntimeError("Only sqlite DB_URL supported in this setup")
    return url.replace("sqlite:///", "/", 1)

_DB_PATH = _db_path_from_url(DB_URL)

def init_db() -> None:
    os.makedirs(os.path.dirname(_DB_PATH), exist_ok=True)
    with sqlite3.connect(_DB_PATH) as con:
        con.execute("PRAGMA journal_mode=WAL;")
        con.execute("PRAGMA synchronous=NORMAL;")
        con.execute("""
        CREATE TABLE IF NOT EXISTS scene_state (
            user_id INTEGER PRIMARY KEY,
            last_scene TEXT NOT NULL,
            last_reflect TEXT,
            updated_at TEXT NOT NULL
        )
        """)
        con.execute("""
        CREATE TABLE IF NOT EXISTS webhook_seen (
            update_id INTEGER PRIMARY KEY,
            seen_at TEXT NOT NULL
        )
        """)
        -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        -- НОВОЕ: журнал отражений
        con.execute("""
        CREATE TABLE IF NOT EXISTS reflections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            text TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """)
        con.commit()

@dataclass
class SceneRow:
    user_id: int
    last_scene: str
    last_reflect: str | None
    updated_at: str

def get_scene(user_id: int) -> SceneRow | None:
    with _lock, sqlite3.connect(_DB_PATH) as con:
        cur = con.execute(
            "SELECT user_id,last_scene,last_reflect,updated_at FROM scene_state WHERE user_id=?",
            (user_id,)
        )
        row = cur.fetchone()
        return SceneRow(*row) if row else None

def upsert_scene(user_id: int, last_scene: str, last_reflect: str | None = None) -> None:
    ts = datetime.utcnow().isoformat() + "Z"
    with _lock, sqlite3.connect(_DB_PATH) as con:
        con.execute("""
        INSERT INTO scene_state(user_id,last_scene,last_reflect,updated_at)
        VALUES(?,?,?,?)
        ON CONFLICT(user_id) DO UPDATE SET
          last_scene=excluded.last_scene,
          last_reflect=excluded.last_reflect,
          updated_at=excluded.updated_at
        """, (user_id, last_scene, last_reflect, ts))
        con.commit()

def is_duplicate_update(update_id: int) -> bool:
    with _lock, sqlite3.connect(_DB_PATH) as con:
        cur = con.execute("SELECT 1 FROM webhook_seen WHERE update_id=?", (update_id,))
        if cur.fetchone():
            return True
        con.execute(
            "INSERT INTO webhook_seen(update_id, seen_at) VALUES(?, ?)",
            (update_id, datetime.utcnow().isoformat() + "Z"),
        )
        con.commit()
        return False

# -------- НОВОЕ: отражения и статус --------

def add_reflection(user_id: int | None, text: str) -> None:
    ts = datetime.utcnow().isoformat() + "Z"
    with _lock, sqlite3.connect(_DB_PATH) as con:
        con.execute(
            "INSERT INTO reflections(user_id,text,created_at) VALUES(?,?,?)",
            (user_id, text.strip(), ts)
        )
        con.commit()

def get_last_reflection() -> tuple[str | None, str | None]:
    with _lock, sqlite3.connect(_DB_PATH) as con:
        cur = con.execute(
            "SELECT text,created_at FROM reflections ORDER BY id DESC LIMIT 1"
        )
        row = cur.fetchone()
        return (row[0], row[1]) if row else (None, None)

def get_status_snapshot() -> dict:
    with _lock, sqlite3.connect(_DB_PATH) as con:
        users = con.execute("SELECT COUNT(*) FROM scene_state").fetchone()[0]
        counts = {k: 0 for k in ("intro","reflect","transition")}
        for k, v in con.execute("""
            SELECT last_scene, COUNT(*) FROM scene_state GROUP BY last_scene
        """).fetchall():
            if k in counts:
                counts[k] = v
        last_reflect, last_reflect_at = get_last_reflection()
        last_updated = con.execute("""
            SELECT COALESCE(MAX(updated_at),'') FROM scene_state
        """).fetchone()[0]
    return {
        "ok": True,
        "users": users,
        "scenes": counts,
        "last_updated": last_updated or None,
        "last_reflect": last_reflect,
        "last_reflect_at": last_reflect_at,
    }
