from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Literal
import os

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field, ValidationError

router = APIRouter(prefix="/api", tags=["api"])

# ---------- GUARD ----------
GUARD_KEY = os.getenv("GUARD_KEY", "").strip()

def _check_guard(x_guard_key: str | None) -> None:
    if not GUARD_KEY:
        return
    if (x_guard_key or "").strip() != GUARD_KEY:
        raise HTTPException(status_code=401, detail="invalid guard key")


# ---------- CORE / STATE ----------
try:
    from app.core.state import STATE  # type: ignore
except Exception:
    class _MiniState:
        def __init__(self) -> None:
            self.core = {
                "cycle": 0,
                "last_update": "-",
                "intro": 0,
                "reflect": 0,
                "transition": 0,
                "events": [],
                "reflection": {"text": "", "updated_at": "-"},
            }

        def snapshot(self):
            return self.core

        def set_core(self, core):
            self.core = core

    STATE = _MiniState()  # type: ignore


def _get_core() -> dict[str, Any]:
    if hasattr(STATE, "snapshot"):
        return STATE.snapshot()
    if hasattr(STATE, "core"):
        return STATE.core
    return {
        "cycle": 0,
        "last_update": "-",
        "intro": 0,
        "reflect": 0,
        "transition": 0,
        "events": [],
        "reflection": {"text": "", "updated_at": "-"},
    }


def _set_core(core: dict[str, Any]) -> None:
    if hasattr(STATE, "set_core"):
        STATE.set_core(core)
    elif hasattr(STATE, "core"):
        STATE.core = core


def _utc_now_iso():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


# ---------- MODELS ----------
SourceType = Literal["ui", "bot", "core"]
SceneType = Literal["intro", "reflect", "transition"]

class EventIn(BaseModel):
    source: SourceType = "ui"
    scene: SceneType
    payload: dict[str, Any] = Field(default_factory=dict)

class EventOut(BaseModel):
    ts: str
    cycle: int
    source: SourceType
    scene: SceneType
    payload: dict[str, Any]


# ---------- ROUTES ----------
@router.get("/healthz")
async def healthz():
    return {"ok": True}


@router.get("/status")
async def get_status():
    return {"ok": True, "core": _get_core()}


@router.get("/timeline")
async def get_timeline():
    core = _get_core()
    events = list(core.get("events", []))
    return {"ok": True, "events": events}


@router.post("/event")
async def post_event(
    body: dict[str, Any],
    x_guard_key: str | None = Header(default=None, convert_underscores=False),
):
    _check_guard(x_guard_key)

    try:
        event_in = EventIn.model_validate(body)
    except ValidationError as e:
        raise HTTPException(
            status_code=422,
            detail={"ok": False, "error": "invalid event schema", "details": e.errors()},
        )

    core = _get_core()
    core.setdefault("cycle", 0)
    core.setdefault("events", [])
    core.setdefault("intro", 0)
    core.setdefault("reflect", 0)
    core.setdefault("transition", 0)

    cycle = core["cycle"] + 1
    ts = _utc_now_iso()

    event_full = EventOut(
        ts=ts,
        cycle=cycle,
        source=event_in.source,
        scene=event_in.scene,
        payload=event_in.payload,
    ).model_dump()

    core["cycle"] = cycle
    core["last_update"] = ts
    core[event_in.scene] += 1

    events = list(core["events"])
    events.append(event_full)
    core["events"] = events[-20:]

    _set_core(core)

    return {"ok": True, "event": event_full}
