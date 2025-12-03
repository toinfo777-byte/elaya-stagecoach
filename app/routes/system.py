from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import logging
import os

from fastapi import APIRouter, Header, HTTPException, Query
from pydantic import BaseModel

from app.core.timeline import add_event, get_timeline
from app.training_progress import add_training_day, get_progress_summary

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
        # временный лог, чтобы видеть, что реально прилетает
        logging.warning(
            "GUARD FAIL: header=%r, expected=%r",
            x_guard_key,
            GUARD_KEY,
        )
        raise HTTPException(status_code=403, detail="Forbidden")


# --- Модели --------------------------------------------------------


class TimelineEvent(BaseModel):
    source: str
    scene: str
    payload: Dict[str, Any] = {}


class TrainingDay(BaseModel):
    user_id: int
    date: str  # ISO-строка даты: 'YYYY-MM-DD'
    vector: str
    reflect: str
    transition: str
    review: str


# --- Healthcheck ---------------------------------------------------


@router.get("/healthz")
async def healthz() -> Dict[str, Any]:
    """
    Простой healthcheck для Render.
    """
    return {
        "status": "ok",
        "ts": datetime.now(timezone.utc).isoformat(),
    }


# --- Таймлайн ядра -------------------------------------------------


@router.post("/event")
async def api_event(
    event: TimelineEvent,
    x_guard_key: Optional[str] = Header(default=None, alias="X-Guard-Key"),
) -> Dict[str, Any]:
    """
    Приём события от тренера / других источников.
    """
    _check_guard(x_guard_key)

    add_event(
        source=event.source,
        scene=event.scene,
        payload=event.payload,
    )

    return {"ok": True}


@router.get("/timeline")
async def api_timeline(
    limit: int = Query(100, ge=1, le=1000),
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Получить последние события таймлайна.
    """
    events = get_timeline(limit=limit)
    return {"events": events}


# --- Тренировки ----------------------------------------------------


@router.post("/training/day")
async def api_training_day(
    body: TrainingDay,
    x_guard_key: Optional[str] = Header(default=None, alias="X-Guard-Key"),
) -> Dict[str, Any]:
    """
    Регистрация одного дня тренировки.
    """
    _check_guard(x_guard_key)

    add_training_day(
        user_id=body.user_id,
        date=body.date,
        vector=body.vector,
        reflect=body.reflect,
        transition=body.transition,
        review=body.review,
    )

    return {"ok": True}


@router.get("/training/progress")
async def api_training_progress(
    user_id: int = Query(..., description="ID пользователя"),
) -> Dict[str, Any]:
    """
    Сводка по прогрессу тренировок.
    """
    summary = get_progress_summary(user_id=user_id)
    return summary
