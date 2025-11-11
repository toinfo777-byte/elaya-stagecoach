# app/core/db.py
from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Any, Dict

DB_PATH = os.getenv("SQLITE_PATH", "/data/elaya.db")

# гарантируем каталог
Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_schema() -> None:
    conn = get_conn()
    cur = conn.cursor()

    # ядро — одна строка с агрегатами
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS core_state (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            users INTEGER NOT NULL DEFAULT 0,
            intro INTEGER NOT NULL DEFAULT 0,
            reflect INTEGER NOT NULL DEFAULT 0,
            transition INTEGER NOT NULL DEFAULT 0,
            last_updated TEXT NOT NULL DEFAULT ''
        );
        """
    )
    cur.execute("INSERT OR IGNORE INTO core_state (id) VALUES (1);")

    # reflection — последняя заметка
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS reflection (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            text TEXT NOT NULL DEFAULT '',
            updated_at TEXT NOT NULL DEFAULT ''
        );
        """
    )
    cur.execute("INSERT OR IGNORE INTO reflection (id) VALUES (1);")

    conn.commit()
    conn.close()


def read_state() -> Dict[str, Any]:
    conn = get_conn()
    cur = conn.cursor()
    core = cur.execute("SELECT * FROM core_state WHERE id = 1").fetchone()
    refl = cur.execute("SELECT * FROM reflection WHERE id = 1").fetchone()
    conn.close()
    return {
        "core": dict(core) if core else {},
        "reflection": dict(refl) if refl else {},
    }


def save_reflection(text: str, updated_at: str) -> None:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE reflection SET text = ?, updated_at = ? WHERE id = 1",
        (text, updated_at),
    )
    conn.commit()
    conn.close()


def bump_core(delta_users=0, delta_intro=0, delta_reflect=0, delta_transition=0, last_updated: str | None = None) -> None:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE core_state
           SET users = MAX(users + ?, 0),
               intro = MAX(intro + ?, 0),
               reflect = MAX(reflect + ?, 0),
               transition = MAX(transition + ?, 0),
               last_updated = COALESCE(?, last_updated)
         WHERE id = 1
        """,
        (delta_users, delta_intro, delta_reflect, delta_transition, last_updated),
    )
    conn.commit()
    conn.close()
