# web/app/routes/system.py
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional

import os

from fastapi import APIRouter, Header, HTTPException, Query, Response
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
        raise HTTPException(status_code=403, detail="Forbidden")


# --- МОДЕЛИ --------------------------------------------------------


class TimelineEvent(BaseModel):
    source: str
    scene: str
    payload: Dict[str, Any] | None = None


# --- POST /api/event -----------------------------------------------


@router.post("/event", status_code=204)
async def post_event(
    event: TimelineEvent,
    x_guard_key: Optional[str] = Header(None),
) -> Response:
    """
    Приём событий таймлайна от тренера и других источников.
    """

    _check_guard(x_guard_key)

    # 1) Всегда пишем в таймлайн
    add_event(
        source=event.source,
        scene=event.scene,
        payload=event.payload or {},
    )

    # 2) Дополнительно: фиксируем тренировочный день
    #    по событию trainer.day.finish
    if event.source == "trainer" and event.scene == "trainer.day.finish":
        payload = event.payload or {}
        tg_user_id = payload.get("tg_user_id")
        if tg_user_id:
            try:
                tg_user_id_int = int(tg_user_id)
                add_training_day(tg_user_id_int)
            except (TypeError, ValueError):
                # тихо игнорируем странный id
                pass

    return Response(status_code=204)


# --- GET /api/progress ---------------------------------------------


@router.get("/progress")
async def get_progress(
    tg_user_id: int = Query(..., description="Telegram User ID"),
    x_guard_key: Optional[str] = Header(None),
):
    """
    Возвращает сводку прогресса по пользователю.

    Ожидаемый формат ответа:
      {
        "total_days": int,
        "current_streak": int
      }
    """
    _check_guard(x_guard_key)
    summary = get_progress_summary(tg_user_id)
    return summary


# --- ВСПОМОГАТЕЛЬНЫЕ ЭНДПОИНТЫ ------------------------------------


@router.get("/timeline")
async def api_timeline(limit: int = 50):
    """
    Простой просмотр таймлайна (для отладки).
    """
    return get_timeline(limit=limit)


@router.get("/status")
async def status():
    """
    Статус ядра — для /api/status.
    """
    now = datetime.now(timezone.utc).isoformat()
    return {
        "status": "ok",
        "time": now,
        "version": "core-0.5.x",
        "build": "manual",
        "profile": "hq",
    }


@router.get("/health")
async def health():
    """
    Технический healthcheck для /api/health.
    """
    return {"status": "ok"}
