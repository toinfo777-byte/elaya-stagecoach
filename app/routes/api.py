# app/routes/api.py
from __future__ import annotations

from datetime import datetime, timezone, date
from typing import Any, Dict, List, Optional, Union
import os

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

from app.core.cycle_state import CycleState
from app import training_progress

router = APIRouter(prefix="/api", tags=["api"])

# -------------------------------------------------
# Health-check
# -------------------------------------------------


@router.get("/healthz")
@router.get("/healthhz")  # alias под опечатку в Render health-check
def healthz() -> Dict[str, Union[bool, str]]:
    """
    Простой health-check.

    /api/healthz  — нормальный путь
    /api/healthhz — alias для Render, который сейчас шлёт запрос именно сюда.
    """
    return {"ok": True, "status": "healthy"}


# -------------------------------------------------
# GUARD защита для мутаций
# -------------------------------------------------

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


# -------------------------------------------------
# /sync — состояние цикла
# -------------------------------------------------


class SyncResponse(BaseModel):
    cycle: int
    server_time: int


@router.get("/sync", response_model=SyncResponse)
async def sync() -> SyncResponse:
    """
    Возвращает текущее состояние цикла и время сервера.
    """
    state = CycleState.get()
    now_ts = int(datetime.now(tz=timezone.utc).timestamp())
    return SyncResponse(cycle=state.cycle, server_time=now_ts)


# -------------------------------------------------
# /event — основной вход событий тренера
# -------------------------------------------------


class TimelineEvent(BaseModel):
    source: str
    scene: str
    payload: Dict[str, Any] = Field(default_factory=dict)


# Легаси-таймлайн для совместимости / отладки
TIMELINE: List[TimelineEvent] = []


@router.post("/event")
async def api_event(
    ev: TimelineEvent,
    x_guard_key: Optional[str] = Header(None),
) -> Dict[str, Any]:
    """
    Принимаем событие от любых источников (бот, ручные тесты и т.д.),
    пишем его в таймлайн и, при необходимости, обновляем служебные данные.
    """
    _check_guard(x_guard_key)

    # 1. Всегда пишем в таймлайн
    TIMELINE.append(ev)

    state = CycleState.get()
    state.append_event(ev.source, ev.scene, ev.payload)

    # 2. Хук для тренера: завершаем тренировку дня -> фиксируем тренировочный день
    if ev.source == "trainer" and ev.scene in ("trainer:done", "trainer.day.finish"):
        payload = ev.payload or {}

        user_id_raw = payload.get("user_id")
        date_str = payload.get("date")

        try:
            uid = int(user_id_raw) if user_id_raw is not None else None
        except (TypeError, ValueError):
            uid = None

        if uid is not None:
            d: Optional[date] = None
            if date_str:
                try:
                    d = date.fromisoformat(date_str)
                except (TypeError, ValueError):
                    d = None

            # ✅ Записываем день в training_progress.json
            training_progress.add_training_day(user_id=uid, d=d)

    return {"status": "ok"}


# -------------------------------------------------
# Легаси /api/timeline — обёртка для совместимости
# -------------------------------------------------


class TimelinePost(BaseModel):
    scene: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    source: str = "api"


@router.get("/timeline", response_model=List[TimelineEvent])
async def get_timeline() -> List[TimelineEvent]:
    """
    Легаси-метод для получения списка событий.
    """
    return TIMELINE


@router.post("/timeline")
async def post_timeline(
    item: TimelinePost,
    x_guard_key: Optional[str] = Header(default=None, alias="X-Guard-Key"),
) -> Dict[str, str]:
    """
    Легаси-метод для записи события в таймлайн.
    Внутри использует ту же логику, что и /api/event.
    """
    _check_guard(x_guard_key)

    event = TimelineEvent(
        source=item.source,
        scene=item.scene,
        payload=item.payload,
    )
    TIMELINE.append(event)

    state = CycleState.get()
    state.append_event(event.source, event.scene, event.payload)

    # Старая логика: если сцена "transition" — считаем это днём тренировки
    if event.scene == "transition":
        user_id = int(event.payload.get("user_id", 1))
        training_progress.add_training_day(user_id)

    return {"status": "ok"}


# -------------------------------------------------
# /progress — прогресс по тренировкам
# -------------------------------------------------


class ProgressResponse(BaseModel):
    user_id: int
    total_days: int
    current_streak: int
    last_date: Optional[str] = None


@router.get("/progress", response_model=ProgressResponse)
async def get_progress(user_id: int) -> ProgressResponse:
    """
    Возвращает прогресс пользователя:

    - total_days     — всего дней с тренировкой
    - current_streak — текущая серия без пропусков
    - last_date      — дата последней тренировки (ISO) или null
    """
    summary = training_progress.get_progress_summary(user_id)

    return ProgressResponse(
        user_id=user_id,
        total_days=summary["total_days"],
        current_streak=summary["current_streak"],
        last_date=summary["last_date"],
    )
