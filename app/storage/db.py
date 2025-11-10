import os, sqlite3, threading, time
from typing import Optional, Tuple

_SQLITE_PATH = os.getenv("SQLITE_PATH", "/data/elaya.db")
_INIT_SQL = """
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS scene_state (
  user_id     INTEGER PRIMARY KEY,
  last_scene  TEXT,
  last_reflect TEXT,
  updated_at  INTEGER
);
CREATE TABLE IF NOT EXISTS webhook_seen (
  update_id   INTEGER PRIMARY KEY,
  seen_at     INTEGER
);
CREATE INDEX IF NOT EXISTS idx_webhook_seen_seen_at ON webhook_seen(seen_at);
"""

_lock = threading.Lock()

def _connect():
    conn = sqlite3.connect(_SQLITE_PATH, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn

_conn = None

def ensure_db():
    global _conn
    with _lock:
        if _conn is None:
            os.makedirs(os.path.dirname(_SQLITE_PATH), exist_ok=True)
            _conn = _connect()
            _conn.executescript(_INIT_SQL)
            _conn.commit()
    return _conn

def save_scene(user_id: int, scene: Optional[str], reflect: Optional[str]):
    conn = ensure_db()
    now = int(time.time())
    with conn:
        cur = conn.execute("SELECT 1 FROM scene_state WHERE user_id=?", (user_id,))
        if cur.fetchone():
            conn.execute(
                "UPDATE scene_state SET last_scene=COALESCE(?, last_scene), last_reflect=COALESCE(?, last_reflect), updated_at=? WHERE user_id=?",
                (scene, reflect, now, user_id),
            )
        else:
            conn.execute(
                "INSERT INTO scene_state(user_id,last_scene,last_reflect,updated_at) VALUES (?,?,?,?)",
                (user_id, scene, reflect, now),
            )

def get_scene(user_id: int) -> Tuple[Optional[str], Optional[str], Optional[int]]:
    conn = ensure_db()
    cur = conn.execute(
        "SELECT last_scene,last_reflect,updated_at FROM scene_state WHERE user_id=?",
        (user_id,),
    )
    row = cur.fetchone()
    return (row[0], row[1], row[2]) if row else (None, None, None)

def is_duplicate(update_id: int, ttl_sec: int) -> bool:
    """True, если update_id уже видели за последние ttl_sec."""
    conn = ensure_db()
    now = int(time.time())
    cutoff = now - ttl_sec
    with conn:
        # Чистим старые хвосты по ходу
        conn.execute("DELETE FROM webhook_seen WHERE seen_at < ?", (cutoff,))
        cur = conn.execute("SELECT 1 FROM webhook_seen WHERE update_id=?", (update_id,))
        if cur.fetchone():
            return True
        conn.execute("INSERT OR IGNORE INTO webhook_seen(update_id, seen_at) VALUES (?,?)", (update_id, now))
    return False
