from __future__ import annotations

import asyncio
import os
import time
from typing import Optional


def format_uptime(start_monotonic: float) -> str:
    """Читабельный аптайм по монотонным часам."""
    seconds = int(time.monotonic() - start_monotonic)
    d, r = divmod(seconds, 86400)
    h, r = divmod(r, 3600)
    m, s = divmod(r, 60)
    parts = []
    if d:
        parts.append(f"{d}d")
    if d or h:
        parts.append(f"{h}h")
    if d or h or m:
        parts.append(f"{m}m")
    parts.append(f"{s}s")
    return " ".join(parts)


def task_by_name(name: str) -> Optional[asyncio.Task]:
    """Пробуем найти запущенную задачу по имени (например, 'cronitor-heartbeat')."""
    try:
        for t in asyncio.all_tasks():
            if t.get_name() == name:
                return t
    except Exception:
        pass
    return None


def sentry_configured() -> bool:
    dsn = (os.getenv("SENTRY_DSN") or "").strip()
    return bool(dsn)


def cronitor_configured() -> bool:
    url = (os.getenv("HEALTHCHECKS_URL") or "").strip()
    return bool(url)


def admin_chat_ids() -> list[int]:
    """Список ID админов из ENV: ADMIN_CHAT_IDS='123,456' или ADMIN_CHAT_ID='123'."""
    raw = os.getenv("ADMIN_CHAT_IDS") or os.getenv("ADMIN_CHAT_ID") or ""
    ids: list[int] = []
    for chunk in raw.replace(";", ",").split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        try:
            ids.append(int(chunk))
        except ValueError:
            continue
    return ids
