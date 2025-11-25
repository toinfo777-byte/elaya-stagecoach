# app/routes/system.py
from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api", tags=["api"])

# --- простая защита для POST (если GUARD_KEY задан) ---

GUARD_KEY = os.getenv("GUARD_KEY", "").strip()


def _check_guard(x_guard_key: Optional[str]) -> None:
    """
    Если GUARD_KEY не задан в окружении — защита выключена.
    Если задан — все POST-запросы с изменением состояния должны
    присылать заголовок X-Guard-Key.
    """
    if not GUARD_KEY:
        return

    if (x_guard_key or "").strip() != GUARD_KEY:
        raise HTTPException(status_code=401, detail="invalid guard key")


# --- модели событий таймлайна ---

class TimelineEventIn(BaseModel):
    source: str
    scene: str
    payload: Dict[str, Any] = {}


class TimelineEventOut(TimelineEventIn):
    ts: datetime


# in-memory хранилище (на каждый процесс)
TIMELINE: List[TimelineEventOut] = []


def _add_event(evt: TimelineEventIn) -> TimelineEventOut:
    event = TimelineEventOut(
        ts=datetime.now(timezone.utc),
        source=evt.source,
        scene=evt.scene,
        payload=evt.payload or {},
    )
    TIMELINE.append(event)
    return event


# --- API ---

@router.get("/timeline")
async def get_timeline(limit: int = 50) -> Dict[str, Any]:
    """
    Вернуть последние события таймлайна.
    """
    # конвертим в dict, чтобы всё было сериализуемо
    events = [e.dict() for e in TIMELINE[-limit:]]
    return {
        "ok": True,
        "events": events,
    }


@router.post("/timeline")
async def post_timeline(
    event: TimelineEventIn,
    x_guard_key: Optional[str] = Header(default=None, alias="X-Guard-Key"),
) -> Dict[str, Any]:
    """
    Добавить событие в таймлайн.
    """
    _check_guard(x_guard_key)
    _add_event(event)
    return {"ok": True}


@router.post("/event")
async def post_event(
    event: TimelineEventIn,
    x_guard_key: Optional[str] = Header(default=None, alias="X-Guard-Key"),
) -> Dict[str, Any]:
    """
    Алиас для /api/timeline, чтобы CLI/бот могли стучаться и так, и так.
    """
    _check_guard(x_guard_key)
    _add_event(event)
    return {"ok": True}

# app/routes/system.py

@router.post("/timeline")
async def post_timeline(
    event: TimelineEventIn,
    x_guard_key: Optional[str] = Header(default=None, alias="X-Guard-Key"),
) -> Dict[str, Any]:
    """
    Добавить событие в таймлайн.
    """
    _check_guard(x_guard_key)

    # 🔍 лог при любом POST
    print(f"[core] timeline POST: source={event.source}, scene={event.scene}, payload={event.payload}")

    _add_event(event)
    return {"ok": True}

@router.get("/timeline/test-add")
async def test_add() -> Dict[str, Any]:
    evt = _add_event(TimelineEventIn(source="test", scene="ping", payload={"hello": "world"}))
    return {"ok": True, "event": evt.dict()}
