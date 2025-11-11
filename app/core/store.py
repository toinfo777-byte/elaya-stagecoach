# app/core/store.py
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
    """
    Поддерживаем только sqlite:* URL. Преобразуем в путь файловой БД.
    Примеры:
      sqlite:////abs/path.db  -> /abs/path.db
      sqlite:///relative.db   -> /relative.db
    """
    if not url.startswith("sqlite:"):
        raise RuntimeError("Only sqlite DB_URL supported in this setup")
    return url.replace("sqlite:///", "/", 1)


_DB_PATH = _db_path_from_url(DB_URL)


# --- schema & init ----------------------------------------------------------
def init_db() -> None:
    """
    Создаёт структуру БД (если нет) и включает режимы устойчивости.
    """
    os.makedirs(os.path.dirname(_DB_PATH), exist_ok=True)
    with sqlite3.connect(_DB_PATH) as con:
        # немного устойчивости под веб-нагрузку
        con.execute("PRAGMA journal_mode=WAL;")
        con.execute("PRAGMA synchronous=NORMAL;")

        con.execute(
            """
            CREATE TABLE IF NOT EXISTS scene_state (
                user_id      INTEGER PRIMARY KEY,
                last_scene   TEXT    NOT NULL,
                last_reflect TEXT,
                updated_at   TEXT    NOT NULL
            )
            """
        )
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS webhook_seen (
                update_id INTEGER PRIMARY KEY,
                seen_at   TEXT NOT NULL
            )
            """
        )
        con.commit()


# --- models -----------------------------------------------------------------
@dataclass
class SceneRow:
    user_id: int
    last_scene: str
    last_reflect: str | None
    updated_at: str


# --- scene state ------------------------------------------------------------
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
              last_scene  = excluded.last_scene,
              last_reflect= excluded.last_reflect,
              updated_at  = excluded.updated_at
            """,
            (user_id, last_scene, last_reflect, ts),
        )
        con.commit()


def add_reflection(user_id: int, reflection: str) -> None:
    """
    Фиксирует последнюю рефлексию пользователя и обновляет updated_at.
    Не создаёт строку заново — предполагается, что upsert_scene уже вызывался.
    """
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


# --- idempotency for webhook ------------------------------------------------
def is_duplicate_update(update_id: int) -> bool:
    """
    True, если update_id уже видели. Иначе пометит как увиденный и вернёт False.
    """
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


# --- metrics & stats --------------------------------------------------------
def get_stats() -> dict:
    """
    Агрегаты для панели HQ и Pulse.

    Возвращает *два* набора ключей:
      — новый API:
          users, last_update, counts{intro,reflect,transition}, last_reflection{text,at}
      — старые имена для обратной совместимости:
          users, last_updated, scene_counts{...}, last_reflect
    """
    with _lock, sqlite3.connect(_DB_PATH) as con:
        con.row_factory = sqlite3.Row

        # users / last_update
        row = con.execute(
            "SELECT COUNT(*) AS users_cnt, MAX(updated_at) AS last_update FROM scene_state"
        ).fetchone()
        users_cnt = int(row["users_cnt"] or 0)
        last_update = row["last_update"]

        # counts by last_scene
        counts = {"intro": 0, "reflect": 0, "transition": 0}
        for r in con.execute(
            "SELECT last_scene, COUNT(*) AS c FROM scene_state GROUP BY last_scene"
        ):
            key = r["last_scene"]
            if key in counts:
                counts[key] = int(r["c"] or 0)

        # last non-empty reflection (most recent)
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

    # новый словарь
    result_new = {
        "users": users_cnt,
        "last_update": last_update,
        "counts": counts,
        "last_reflection": {
            "text": last_reflect,
            "at": last_reflect_at,
        },
    }
    # совместимость со старой главной
    result_old = {
        "users": users_cnt,
        "last_updated": last_update,
        "scene_counts": counts,
        "last_reflect": last_reflect or None,
    }
    result_new.update(result_old)
    return result_new
