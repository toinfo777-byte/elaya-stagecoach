import os, shutil, sqlite3
from datetime import datetime, timezone
from pathlib import Path
from app.config import settings

def _sqlite_path() -> str | None:
    url = (settings.db_url or "").lower()
    if not url.startswith("sqlite"):
        return None
    # sqlite:////data/elaya.db  -> берём часть после '///'
    return url.split("///", 1)[1] if "///" in url else None

def backup_sqlite(retention_days: int = 7) -> str:
    db = _sqlite_path()
    if not db or not os.path.exists(db):
        return "no sqlite db"

    dst_dir = "/data/backups"
    os.makedirs(dst_dir, exist_ok=True)

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d")
    dst = os.path.join(dst_dir, f"elaya-{stamp}.db")
    shutil.copy2(db, dst)

    # чистим старше retention_days
    now = datetime.now(timezone.utc)
    for p in Path(dst_dir).glob("elaya-*.db"):
        try:
            if (now - datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc)).days > retention_days:
                p.unlink()
        except Exception:
            pass

    return dst

def vacuum_sqlite() -> str:
    db = _sqlite_path()
    if not db or not os.path.exists(db):
        return "no sqlite db"
    con = sqlite3.connect(db)
    con.execute("VACUUM")
    con.close()
    return "ok"
