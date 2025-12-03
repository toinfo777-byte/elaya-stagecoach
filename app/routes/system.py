# app/routes/system.py
from __future__ import annotations

import logging
import os
from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Header, HTTPException, Query
from pydantic import BaseModel, Field

from app.core.timeline import add_event, get_timeline
from app.training_progress import add_training_day, get_progress_summary

router = APIRouter(prefix="/api", tags=["api"])

# --- GUARD ---------------------------------------------------------

GUARD_KEY = os.getenv("GUARD_KEY", "").strip()
logger = logging.getLogger(__name__)


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
        # Диагностика: что реально прилетело и что мы ждём
        logger.warning("GUARD FAIL: header=%r expected=%r", x_guard_key, GUARD_KEY)
        raise HTTPException(status_code=403, detail="Forbidden")


# --- Модели --------------------------------------------------------


class TimelineEvent(BaseModel):
    source: str
    scene: str
    # через Field, чтобы не было общей мутируемой ссылки
    payload: Dict[str, Any] = Field(default_factory=dict)


class TrainingDay(BaseModel):
    user_id: int
    date: date
    vector: str = ""
    reflect: str = ""
    transition: str = ""
    review: str = ""


# --- Эндпоинты ядра -----------------------------------------------


@router.post("/event")
async def api_event(
    event: TimelineEvent,
    x_guard_key: Optional[str] = Header(None, alias="X-Guard-Key"),
) -> Dict[str, Any]:
    """
    Принимает событие от тренера (или других источников) и кладёт в таймлайн.
    """
    _check_guard(x_guard_key)

    # Лог в ядре, чтобы видеть, что именно прилетает
    logger.info(
        "CORE EVENT: source=%s scene=%s payload_keys=%s",
        event.source,
        event.scene,
        list(event.payload.keys()),
    )

    add_event(
        source=event.source,
        scene=event.scene,
        payload=event.payload,
    )

    return {"ok": True}


@router.get("/timeline")
async def api_timeline(
    limit: int = Query(100, ge=1, le=1000),
) -> Dict[str, Any]:
    """
    Возвращает последние события таймлайна.

    Формат оставлен совместимым со старым:
    { "ok": true, "events": [...] }
    """
    items: List[Dict[str, Any]] = get_timeline(limit=limit)
    return {
        "ok": True,
        "events": items,
        "count": len(items),
        "ts": datetime.now(timezone.utc).isoformat(),
    }


@router.post("/trainer/day")
async def api_trainer_day(
    day: TrainingDay,
    x_guard_key: Optional[str] = Header(None, alias="X-Guard-Key"),
) -> Dict[str, Any]:
    """
    Сохранение тренировочного дня (если ты решишь слать сюда агрегированные данные).
    """
    _check_guard(x_guard_key)

    add_training_day(
        user_id=day.user_id,
        date=day.date,
        vector=day.vector,
        reflect=day.reflect,
        transition=day.transition,
        review=day.review,
    )

    return {"ok": True}


@router.get("/trainer/progress")
async def api_trainer_progress(
    user_id: int = Query(..., ge=1),
) -> Dict[str, Any]:
    """
    Сводка по прогрессу конкретного пользователя.
    """
    summary = get_progress_summary(user_id=user_id)
    return {
        "ok": True,
        "data": summary,
    }
