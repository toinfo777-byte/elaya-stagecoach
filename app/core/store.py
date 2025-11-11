from __future__ import annotations

import os
import sqlite3
import threading
from dataclasses import dataclass
from datetime import datetime

# --- config -----------------------------------------------------------------
DB_URL = os.getenv("DB_URL", "sqlite:////data/elaya.db")

_lock = threading.RLock()


def _db_path_from_url(url: str) -> str:
    if not url.startswith("sqlite:"):
        raise RuntimeError("Only sqlite DB_URL supported in this setup")
    # sqlite:////abs/path.db  | sqlite:///relative.db
    return url.replace("sqlite:///", "/", 1)


_DB_PATH = _db_path_from_url(DB_URL)

# --- bootstrap --------------------------------------------------------------
def init_db() -> None:
    os.makedirs(os.path.dirname(_DB_PATH), exist_ok=True)
    with sqlite3.connect(_DB_PATH) as con:
        con.execute("PRAGMA journal_mode=WAL;")
        con.execute("PRAGMA synchronous=NORMAL;")
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS scene_state (
                user_id INTEGER PRIMARY KEY,
                last_scene TEXT NOT NULL,
                last_reflect TEXT,
                updated_at TEXT NOT NULL
            )
            """
        )
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS webhook_seen (
                update_id INTEGER PRIMARY KEY,
                seen_at TEXT NOT NULL
            )
            """
        )
        con.commit()


# --- rows -------------------------------------------------------------------
@dataclass
class SceneRow:
    user_id: int
    last_scene: str
    last_reflect: str | None
    updated_at: str


# --- CRUD -------------------------------------------------------------------
def get_scene(user_id: int) -> SceneRow | None:
    with _lock, sqlite3.connect(_DB_PATH) as con:
        cur = con.execute(
            "SELECT user_id,last_scene,last_reflect,updated_at "
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
            INSERT INTO scene_state(user_id,last_scene,last_reflect,updated_at)
            VALUES(?,?,?,?)
            ON CONFLICT(user_id) DO UPDATE SET
              last_scene=excluded.last_scene,
              last_reflect=excluded.last_reflect,
              updated_at=excluded.updated_at
            """,
            (user_id, last_scene, last_reflect, ts),
        )
        con.commit()


def add_reflection(user_id: int, reflection: str) -> None:
    ts = datetime.utcnow().isoformat() + "Z"
    with _lock, sqlite3.connect(_DB_PATH) as con:
        con.execute(
            """
            UPDATE scene_state
            SET last_reflect=?, updated_at=?
            WHERE user_id=?
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


# --- HQ stats (расширенная) -------------------------------------------------
def get_stats() -> dict:
    with _lock, sqlite3.connect(_DB_PATH) as con:
        con.row_factory = sqlite3.Row

        row = con.execute(
            "SELECT COUNT(*) AS users_cnt, MAX(updated_at) AS last_update FROM scene_state"
        ).fetchone()
        users_cnt = int(row["users_cnt"] or 0)
        last_update = row["last_update"]

        counts = {"intro": 0, "reflect": 0, "transition": 0}
        for r in con.execute(
            "SELECT last_scene, COUNT(*) AS c FROM scene_state GROUP BY last_scene"
        ):
            if r["last_scene"] in counts:
                counts[r["last_scene"]] = int(r["c"] or 0)

        ref = con.execute(
            """
            SELECT last_reflect, updated_at
            FROM scene_state
            WHERE last_reflect IS NOT NULL AND TRIM(last_reflect) <> ''
            ORDER BY updated_at DESC
            LIMIT 1
            """
        ).fetchone()
        last_reflect = ref["last_reflect"] if ref else None
        last_reflect_at = ref["updated_at"] if ref else None

    return {
        "users": users_cnt,
        "last_update": last_update,
        "counts": counts,
        "last_reflection": {"text": last_reflect, "at": last_reflect_at},
    }


# --- HQ stats (компактная для /ui/stats.json) -------------------------------
def get_scene_stats() -> dict:
    with _lock, sqlite3.connect(_DB_PATH) as con:
        counts = {"intro": 0, "reflect": 0, "transition": 0}
        for scene, cnt in con.execute(
            "SELECT last_scene, COUNT(*) FROM scene_state GROUP BY last_scene"
        ).fetchall():
            if scene in counts:
                counts[scene] = int(cnt)

        last_updated = con.execute(
            "SELECT MAX(updated_at) FROM scene_state"
        ).fetchone()[0]

        last_reflection = con.execute(
            """
            SELECT last_reflect
            FROM scene_state
            WHERE last_reflect IS NOT NULL AND TRIM(last_reflect) <> ''
            ORDER BY updated_at DESC
            LIMIT 1
            """
        ).fetchone()
        last_reflection = last_reflection[0] if last_reflection else None

    return {
        "counts": counts,
        "last_updated": last_updated,
        "last_reflection": last_reflection,
    }


# --- Aggregates for UI / Pulse ----------------------------------------------
def get_counts() -> dict:
    with _lock, sqlite3.connect(_DB_PATH) as con:
        cur = con.execute("SELECT COUNT(*) FROM scene_state")
        users = cur.fetchone()[0] or 0

        cur = con.execute(
            """
            SELECT last_scene, COUNT(*)
            FROM scene_state
            GROUP BY last_scene
            """
        )
        by_scene = {row[0]: row[1] for row in cur.fetchall()}

        cur = con.execute("SELECT COALESCE(MAX(updated_at), '') FROM scene_state")
        last_updated = cur.fetchone()[0] or ""

    return {
        "users": users,
        "intro": by_scene.get("intro", 0),
        "reflect": by_scene.get("reflect", 0),
        "transition": by_scene.get("transition", 0),
        "last_updated": last_updated,
    }


def get_last_reflection() -> dict | None:
    with _lock, sqlite3.connect(_DB_PATH) as con:
        cur = con.execute(
            """
            SELECT user_id, last_reflect, updated_at
            FROM scene_state
            WHERE last_reflect IS NOT NULL AND TRIM(last_reflect) <> ''
            ORDER BY updated_at DESC
            LIMIT 1
            """
        )
        row = cur.fetchone()
        if not row:
            return None
        return {"user_id": row[0], "text": row[1], "updated_at": row[2]}
