# app/routes/system.py
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import logging
import os

from fastapi import APIRouter, Header, HTTPException, Query
from pydantic import BaseModel

from app.core.timeline import add_event, get_timeline

router = APIRouter(prefix="/api", tags=["api"])

logger = logging.getLogger(__name__)

# --------------------------------------------------------------
# ENV
# --------------------------------------------------------------

GUARD_KEY = os.getenv("GUARD_KEY", "").strip()
ENV = os.getenv("ENV", "dev")
MODE = os.getenv("MODE", "dev")
IMAGE_TAG = os.getenv("IMAGE_TAG", "dev")


# --------------------------------------------------------------
# GUARD
# --------------------------------------------------------------

def _check_guard(x_guard_key: Optional[str]) -> None:
    """
    Простая защита для мутирующих запросов.
    Если GUARD_KEY не задан — защита выключена.
    """
    if not GUARD_KEY:
        return

    if not x_guard_key or x_guard_key != GUARD_KEY:
        logger.warning(
            "GUARD FAIL: header=%r expected=%r",
            x_guard_key,
            GUARD_KEY,
        )
        raise HTTPException(status_code=403, detail="Forbidden")


# --------------------------------------------------------------
# МОДЕЛЬ СОБЫТИЯ
# --------------------------------------------------------------

class TimelineEvent(BaseModel):
    source: str
    scene: str
    payload: Dict[str, Any] = {}


# --------------------------------------------------------------
# ПРИЁМ СОБЫТИЙ
# --------------------------------------------------------------

@router.post("/event")
def api_event(
    event: TimelineEvent,
    x_guard_key: Optional[str] = Header(default=None, alias="X-Guard-Key"),
) -> Dict[str, str]:
    """
    Приём события от тренера / других сервисов.
    Требует корректного X-Guard-Key, если GUARD_KEY задан.
    """
    _check_guard(x_guard_key)

    add_event(
        source=event.source,
        scene=event.scene,
        payload=event.payload,
    )

    return {"status": "ok"}


# --------------------------------------------------------------
# ЧТЕНИЕ ТАЙМЛАЙНА
# --------------------------------------------------------------

@router.get("/timeline")
def api_timeline(
    limit: int = Query(100, ge=1, le=1000),
) -> List[Dict[str, Any]]:
    """Вернуть последние события таймлайна."""
    return get_timeline(limit=limit)


# --------------------------------------------------------------
# ПОИСК ПОСЛЕДНЕГО trainer-СОБЫТИЯ
# --------------------------------------------------------------

def _get_last_trainer_event() -> Dict[str, Any]:
    """Находит последнее событие с source == 'trainer'."""
    events = get_timeline(limit=200)

    for ev in reversed(events):
        if ev.get("source") == "trainer":
            return ev

    return {}


# --------------------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------------------

@router.get("/health")
def api_health() -> Dict[str, Any]:
    """Внутренний health-check ядра Элайи."""
    now = datetime.now(timezone.utc)

    last_trainer = _get_last_trainer_event()
    trainer_block: Dict[str, Any] = {"has_events": False}

    if last_trainer:
        trainer_ts_raw = last_trainer.get("ts_utc") or last_trainer.get("ts")

        trainer_ts = None
        if isinstance(trainer_ts_raw, str):
            try:
                trainer_ts = datetime.fromisoformat(trainer_ts_raw)
            except Exception:
                trainer_ts = None

        trainer_block = {
            "has_events": True,
            "last_scene": last_trainer.get("scene"),
            "last_source": last_trainer.get("source"),
            "last_timestamp": trainer_ts_raw,
        }

        if trainer_ts and trainer_ts.tzinfo:
            delta = now - trainer_ts
            trainer_block["seconds_since_last_event"] = int(delta.total_seconds())

    return {
        "status": "ok",
        "time_utc": now.isoformat(),
        "env": ENV,
        "mode": MODE,
        "image_tag": IMAGE_TAG,
        "guard_enabled": bool(GUARD_KEY),
        "web": {"status": "ok"},
        "trainer": trainer_block,
    }


# --------------------------------------------------------------
# `/healthz` — короткий alias
# --------------------------------------------------------------

@router.get("/healthz")
def api_healthz() -> Dict[str, Any]:
    return api_health()
