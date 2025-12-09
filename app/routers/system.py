# app/routers/system.py
from __future__ import annotations

import os
from typing import Any, Dict, Optional

from fastapi import APIRouter, Header, HTTPException, Query
from pydantic import BaseModel

from app.core.timeline import add_event, get_timeline

# Это FastAPI-роутер, а не aiogram
router = APIRouter(prefix="/api", tags=["api"])

# --- GUARD ---------------------------------------------------------

GUARD_KEY = os.getenv("GUARD_KEY", "").strip()


def _check_guard(x_guard_key: Optional[str]) -> None:
    """
    Простая защита для мутирующих запросов.

    Если GUARD_KEY не задан в окружении — защита выключена.
    Если задан — все запросы с изменением состояния должны
    присылать заголовок X-Guard-Key.
    """
    if not GUARD_KEY:
        return

    if not x_guard_key or x_guard_key != GUARD_KEY:
        raise HTTPException(status_code=403, detail="Forbidden")


# --- Модели --------------------------------------------------------


class TimelineEvent(BaseModel):
    source: str
    scene: str
    payload: Dict[str, Any] = {}


# --- Эндпоинты -----------------------------------------------------


@router.post("/event")
async def push_event(
    event: TimelineEvent,
    x_guard_key: Optional[str] = Header(None, convert_underscores=False),
) -> Dict[str, Any]:
    """
    Приём события от тренера / CLI / других агентов.
    """
    _check_guard(x_guard_key)

    add_event(
        source=event.source,
        scene=event.scene,
        payload=event.payload,
    )

    return {"ok": True}


@router.get("/timeline")
async def read_timeline(
    limit: int = Query(100, ge=1, le=1000),
) -> Dict[str, Any]:
    """
    Вернуть последние события ядра.
    """
    events = get_timeline(limit=limit)
    return {"ok": True, "events": events}
