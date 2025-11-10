# app/core/store.py
from __future__ import annotations

import os
import sqlite3
import threading
from dataclasses import dataclass
from datetime import datetime

DB_URL = os.getenv("DB_URL", "sqlite:////data/elaya.db")

_lock = threading.RLock()


def _db_path_from_url(url: str) -> str:
    if not url.startswith("sqlite:"):
        raise RuntimeError("Only sqlite DB_URL supported in this setup")
    # sqlite:////abs/path.db  | sqlite:///relative.db
    return url.replace("sqlite:///", "/", 1)


_DB_PATH = _db_path_from_url(DB_URL)


def init_db() -> None:
    os.makedirs(os.path.dirname(_DB_PATH), exist_ok=True)
    with sqlite3.connect(_DB_PATH) as con:
        # немножко устойчивости под веб-нагрузку
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
            "SELECT user_id, last_scene, last_reflect, updated_at "
            "FROM scene_state WHERE user_id=?",
            (user_id,),
        )
        row = cur.fetchone()
        return SceneRow(*row) if row else None


def upsert_scene(user_id: int, last_scene: str, last_reflect: str | None = None) -> None:
    ts = datetime.utcnow().isoformat() + "Z"
    with _lock, sqlite3.connect(_DB_PATH) as con:
        con.execute(
            """
            INSERT INTO scene_state(user_id, last_scene, last_reflect, updated_at)
            VALUES(?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
              last_scene=excluded.last_scene,
              last_reflect=excluded.last_reflect,
              updated_at=excluded.updated_at
            """,
            (user_id, last_scene, last_reflect, ts),
        )
        con.commit()


def add_reflection(user_id: int, reflection: str) -> None:
    """Сохраняет последнюю рефлексию и обновляет updated_at."""
    ts = datetime.utcnow().isoformat() + "Z"
    with _lock, sqlite3.connect(_DB_PATH) as con:
        con.execute(
            """
            UPDATE scene_state
            SET last_reflect = ?, updated_at = ?
            WHERE user_id = ?
            """,
            (reflection.strip(), ts, user_id),
        )
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


# --- metrics & stats ---------------------------------------------------------
def get_stats() -> dict:
    """
    Агрегаты для панели HQ:
    - users: количество пользователей с состоянием
    - last_updated: последний ts из scene_state
    - scene_counts: счётчик по last_scene
    - last_reflect: последняя непустая рефлексия (самая свежая)
    """
    with _lock, sqlite3.connect(_DB_PATH) as con:
        con.row_factory = sqlite3.Row

        cur = con.execute("SELECT COUNT(1) AS c FROM scene_state")
        users = int(cur.fetchone()["c"])

        cur = con.execute("SELECT MAX(updated_at) AS m FROM scene_state")
        last_updated = cur.fetchone()["m"] if users else None

        cur = con.execute("""
            SELECT last_scene, COUNT(1) AS c
            FROM scene_state
            GROUP BY last_scene
        """)
        scene_counts = {row["last_scene"]: int(row["c"]) for row in cur.fetchall()}

        cur = con.execute("""
            SELECT last_reflect
            FROM scene_state
            WHERE last_reflect IS NOT NULL AND TRIM(last_reflect) <> ''
            ORDER BY updated_at DESC
            LIMIT 1
        """)
        row = cur.fetchone()
        last_reflect = row["last_reflect"] if row else None

    return {
        "users": users,
        "last_updated": last_updated,
        "scene_counts": scene_counts,
        "last_reflect": last_reflect,
    }
