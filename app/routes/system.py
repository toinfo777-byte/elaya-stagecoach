from fastapi import APIRouter, Header, HTTPException, Query
from datetime import datetime, timezone
import os

# --- storage (SQLite) ---
from app.core.storage import TimelineStore

router = APIRouter(prefix="/api", tags=["api"])
store = TimelineStore()

# --- защита (только для мутаций) ---
GUARD_KEY = os.getenv("GUARD_KEY", "").strip()


def _check_guard(x_guard_key: str | None):
    if not GUARD_KEY:
        return  # защита отключена
    if (x_guard_key or "").strip() != GUARD_KEY:
        raise HTTPException(status_code=401, detail="invalid guard key")


# --- ядро: работаем через StateStore, если он есть; иначе — минимальный CORE ---
try:
    from app.core.state import StateStore  # ваш класс хранения состояния

    def _core_snapshot():
        return StateStore.get().get_state().snapshot()

    def _core_sync(source: str):
        StateStore.get().sync(source=source)
        return StateStore.get().get_state().snapshot()

except Exception:
    # fallback: простой in-memory
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
async def api_sync(x_guard_key: str | None = Header(default=None, alias="X-Guard-Key")):
    _check_guard(x_guard_key)
    core = _core_sync(source="ui")
    return {"ok": True, "message": "synced", "core": core}


# >>> NEW: timeline (персистентное хранилище событий)
@router.get("/timeline")
async def api_timeline(
    limit: int = Query(200, ge=1, le=1000),
    source: str | None = None,
):
    events = store.get_events(limit=limit, source=source)
    return {"ok": True, "events": events}


@router.post("/timeline")
async def api_timeline_add(
    text: str,
    source: str = "ui",
    x_guard_key: str | None = Header(default=None, alias="X-Guard-Key"),
):
    _check_guard(x_guard_key)
    store.add_event(source=source, text=text)
    return {"ok": True, "message": "event added"}


@router.post("/reflection")
async def api_reflection(
    text: str,
    x_guard_key: str | None = Header(default=None, alias="X-Guard-Key"),
):
    _check_guard(x_guard_key)
    # аккуратно обновляем reflection и добавляем событие
    core = _core_snapshot()
    core.setdefault("reflection", {})
    core["reflection"]["text"] = text
    core["reflection"]["updated_at"] = datetime.now(timezone.utc).isoformat()
    _core_sync(source="reflection")
    # продублируем в timeline (полезно для истории)
    try:
        store.add_event(source="reflection", text=text)
    except Exception:
        pass
    return {"ok": True, "reflection": core["reflection"]}
