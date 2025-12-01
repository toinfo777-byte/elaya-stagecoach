# app/routes/system.py
from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Header, HTTPException, Query
from pydantic import BaseModel

from app.core.cycle_state import CycleState
from app.core.timeline import add_event, get_timeline

# training_progress в ядре у тебя уже был, но делаем импорт мягким
try:
    from app.training_progress import get_progress_summary  # type: ignore
except ImportError:
    get_progress_summary = None  # type: ignore[assignment]

router = APIRouter(prefix="/api", tags=["api"])

# --- Версия ядра ---------------------------------------------------

CORE_VERSION = "0.6.0"

# --- GUARD ---------------------------------------------------------

GUARD_KEY = os.getenv("GUARD_KEY", "").strip()


def _check_guard(x_guard_key: Optional[str]) -> None:
    """
    Простая защита для мутирующих запросов.

    Если GUARD_KEY не задан в окружении — защита выключена.
    Если задан — любые мутирующие запросы (POST /sync, POST /event, ...)
    должны присылать заголовок X-Guard-Key с корректным значением.
    """
    if not GUARD_KEY:
        # защита выключена — разрешаем всё
        return

    if not x_guard_key or x_guard_key != GUARD_KEY:
        raise HTTPException(status_code=403, detail="Forbidden")


# --- Модели --------------------------------------------------------


class TimelineEvent(BaseModel):
    source: str
    scene: str
    payload: Dict[str, Any] = {}


class SyncPayload(BaseModel):
    """
    Минимальная модель для синхронизации состояния цикла.
    CLI/Trainer могут присылать любую полезную инфу в client.
    """
    client: Dict[str, Any] | None = None


# --- Состояние цикла -----------------------------------------------

_cycle_state = CycleState()


def _cycle_snapshot() -> Dict[str, Any]:
    """
    Единая точка, откуда берём состояние цикла для /status и /sync.
    Если в CycleState у тебя другой API — адаптируй здесь.
    """
    if hasattr(_cycle_state, "get_state"):
        return _cycle_state.get_state()  # type: ignore[no-any-return]
    if hasattr(_cycle_state, "to_dict"):
        return _cycle_state.to_dict()  # type: ignore[no-any-return]
    return {}


# --- /status -------------------------------------------------------

@router.get("/status")
async def api_status() -> Dict[str, Any]:
    """
    Лёгкий health-check ядра.
    Формат ответа согласован с /sync.
    """
    return {
        "core_version": CORE_VERSION,
        "server_time": datetime.now(timezone.utc).isoformat(),
        "cycle": _cycle_snapshot(),
    }


# --- /sync ---------------------------------------------------------

@router.post("/sync")
async def api_sync(
    payload: SyncPayload,
    x_guard_key: Optional[str] = Header(None),
) -> Dict[str, Any]:
    """
    Синхронизация состояния с клиентом (CLI, Trainer и т.п.).

    ВСЕГДА под защитой GUARD_KEY.
    """
    _check_guard(x_guard_key)

    client_data = payload.client or {}

    # Если у CycleState есть своя логика обновления — адаптируй.
    if hasattr(_cycle_state, "update_from_client"):
        _cycle_state.update_from_client(client_data)  # type: ignore[arg-type]

    # Ответ в том же формате, что и /status
    return {
        "core_version": CORE_VERSION,
        "server_time": datetime.now(timezone.utc).isoformat(),
        "cycle": _cycle_snapshot(),
    }


# --- /event (таймлайн) ---------------------------------------------

@router.post("/event")
async def api_add_event(
    event: TimelineEvent,
    x_guard_key: Optional[str] = Header(None),
) -> Dict[str, Any]:
    """
    Добавление события в таймлайн ядра.
    Используется Trainer/CLI/etc.
    """
    _check_guard(x_guard_key)

    add_event(
        source=event.source,
        scene=event.scene,
        payload=event.payload,
        ts=datetime.now(timezone.utc),
    )
    return {"status": "ok"}


@router.get("/timeline")
async def api_get_timeline(
    limit: int = Query(50, ge=1, le=500),
) -> Dict[str, Any]:
    """
    Получение последних событий таймлайна.

    ВАЖНО:
    - возвращаем ключ "events", а не "items", чтобы не ломать extended.py
      и прочие места, где уже ожидается data["events"].
    """
    items: List[Dict[str, Any]] = get_timeline(limit=limit)
    return {
        "core_version": CORE_VERSION,
        "events": items,
    }


# --- (опционально) /training/progress ------------------------------

@router.get("/training/progress")
async def api_training_progress() -> Dict[str, Any]:
    """
    Опциональный эндпоинт, если в ядре есть training_progress и
    функция get_progress_summary.
    """
    if get_progress_summary is None:
        raise HTTPException(status_code=501, detail="Training progress disabled")

    summary = get_progress_summary()
    return {
        "core_version": CORE_VERSION,
        "summary": summary,
    }
