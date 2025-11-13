# app/routes/system.py
from fastapi import APIRouter, Header
from datetime import datetime, timezone
import os

router = APIRouter(prefix="/api", tags=["api"])

# --- защита (временно отключена на web) ---
GUARD_KEY = os.getenv("GUARD_KEY", "").strip()


def _check_guard(x_guard_key: str | None):
    """
    ВРЕМЕННО: защита отключена.
    Даже если GUARD_KEY задан в окружении, проверки не выполняются.
    """
    return  # no-op


# --- ядро ---
try:
    from app.core.state import StateStore  # твой стор

    def _core_snapshot():
        return StateStore.get().get_state().snapshot()

    def _core_sync(source: str):
        StateStore.get().sync(source=source)
        return StateStore.get().get_state().snapshot()

except Exception:
    # fallback, если StateStore недоступен
    CORE = {
        "cycle": 0,
        "last_update": "-",
        "intro": 0,
        "reflect": 0,
        "transition": 0,
        "events": [],
        "reflection": {"text": "", "updated_at": "-"},
    }

    def _core_snapshot():
        return CORE

    def _core_sync(source: str):
        CORE["cycle"] += 1
        CORE["last_update"] = datetime.now(timezone.utc).isoformat()
        CORE["events"].append({"source": source, "cycle": CORE["cycle"]})
        return CORE


# --- endpoints ---


@router.get("/status")
async def api_status():
    return {"ok": True, "core": _core_snapshot()}


@router.post("/sync")
async def api_sync(
    x_guard_key: str | None = Header(default=None, alias="X-Guard-Key"),
):
    _check_guard(x_guard_key)
    core = _core_sync(source="ui")
    return {"ok": True, "message": "synced", "core": core}


@router.get("/timeline")
async def api_timeline(limit: int = 50):
    """Возвращает последние события ядра."""
    events = _core_snapshot().get("events", [])
    if not isinstance(events, list):
        events = []
    limit = max(1, min(limit, 500))
    return {"ok": True, "events": events[-limit:]}


@router.post("/reflection")
async def api_reflection(
    text: str,
    x_guard_key: str | None = Header(default=None, alias="X-Guard-Key"),
):
    _check_guard(x_guard_key)
    core = _core_snapshot()
    core.setdefault("reflection", {})
    core["reflection"]["text"] = text
    core["reflection"]["updated_at"] = datetime.now(timezone.utc).isoformat()
    _core_sync(source="reflection")
    return {"ok": True, "reflection": core["reflection"]}
