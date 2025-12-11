# app/routers/system.py
from __future__ import annotations

from datetime import datetime, timezone, date
from typing import Any, Dict, List, Optional
import logging
import os

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

from app.core.timeline import add_event as core_add_event, get_timeline
from app.training_progress import get_progress_summary  # прогресс тренера


router = APIRouter(prefix="/api", tags=["api"])
logger = logging.getLogger(__name__)


# --- ENV ----------------------------------------------------------------------

GUARD_KEY = os.getenv("GUARD_KEY", "").strip()
ENV = os.getenv("ENV", "dev")
MODE = os.getenv("MODE", "dev")
IMAGE_TAG = os.getenv("IMAGE_TAG", "dev")


def _check_guard(x_guard_key: Optional[str]) -> None:
    """
    Простая защита по ключу.
    Если GUARD_KEY не задан — защита выключена.
    Если задан — все мутирующие запросы должны прислать X-Guard-Key.
    """
    if not GUARD_KEY:
        return

    if not x_guard_key or x_guard_key != GUARD_KEY:
        raise HTTPException(status_code=403, detail="Forbidden")


# --- МОДЕЛИ -------------------------------------------------------------------


class TimelineEvent(BaseModel):
    source: str
    scene: str
    payload: Dict[str, Any] = Field(default_factory=dict)


# --- HEALTH -------------------------------------------------------------------


@router.get("/health")
async def api_health() -> Dict[str, Any]:
    """
    Простой health-check для Render и тренера.
    """
    return {
        "status": "ok",
        "env": ENV,
        "mode": MODE,
        "image_tag": IMAGE_TAG,
        "now": datetime.now(timezone.utc).isoformat(),
    }


# --- ПРИЁМ СОБЫТИЙ ------------------------------------------------------------


@router.post("/event")
async def api_event(
    event: TimelineEvent,
    x_guard_key: Optional[str] = Header(None),
) -> Dict[str, Any]:
    """
    Приём события от тренера (и других источников) + запись в таймлайн.
    """
    _check_guard(x_guard_key)

    # 1. Всегда пишем в таймлайн (ядро)
    core_add_event(
        source=event.source,
        scene=event.scene,
        payload=event.payload or {},
    )

    # 2. При желании здесь можем ловить trainer.day.finish и
    #    пересчитывать прогресс, но пока достаточно самого таймлайна.
    logger.info("Timeline event: %s / %s", event.source, event.scene)

    return {"status": "ok"}


# --- ПРОГРЕСС ТРЕНЕРА ---------------------------------------------------------


@router.get("/progress")
def api_progress(
    tg_user_id: int = Query(..., alias="tg_user_id"),
):
    """
    Возвращает сводку прогресса по конкретному пользователю.
    tg_user_id берём из query-параметра и пробрасываем в get_progress_summary.
    """
    return get_progress_summary(user_id=tg_user_id)


# --- (ОПЦИОНАЛЬНО) ТАЙМЛАЙН ---------------------------------------------------


@router.get("/timeline")
async def api_timeline() -> Dict[str, Any]:
    """
    Отладочный просмотр таймлайна (можно вырубить в prod).
    """
    events = get_timeline()
    return {"events": events}
