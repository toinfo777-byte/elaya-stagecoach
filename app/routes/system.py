from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

import os
from fastapi import APIRouter, Header, HTTPException, Query
from pydantic import BaseModel

router = APIRouter(prefix="/api", tags=["api"])

# --- защита (только для мутаций) ---

GUARD_KEY = os.getenv("GUARD_KEY", "").strip()


def _check_guard(x_guard_key: str | None):
    """
    Простая защита для мутаций:
    - если GUARD_KEY не задан в окружении — защита отключена
    - если задан — требуем точное совпадение заголовка X-Guard-Key
    """
    if not GUARD_KEY:
        return  # защита отключена
    if (x_guard_key or "").strip() != GUARD_KEY:
        raise HTTPException(status_code=401, detail="invalid guard key")


# --- модели ядра ---

class Reflection(BaseModel):
    text: str = ""
    updated_at: str = "-"  # ISO-строка или "-"


class Event(BaseModel):
    ts: datetime
    cycle: int
    source: str
    scene: str
    payload: dict[str, Any] = {}


class CoreState(BaseModel):
    cycle: int = 0
    last_update: datetime | None = None

    intro: int = 0
    reflect: int = 0
    transition: int = 0

    events: list[Event] = []
    reflection: Reflection = Reflection()


# одно единственное ядро на процесс
CORE = CoreState()


# --- внутренняя логика работы с ядром ---

def _push_event(*, scene: str, source: str, payload: dict[str, Any]) -> Event:
    """
    Добавляем событие в ядро:
    - при scene="transition" увеличиваем номер цикла
    - обновляем счётчики intro/reflect/transition
    - пишем ts и текущий cycle
    - храним только последние 200 событий
    """
    # обновляем счётчики сцен
    if scene == "intro":
        CORE.intro += 1
    elif scene == "reflect":
        CORE.reflect += 1
    elif scene == "transition":
        CORE.transition += 1
        CORE.cycle += 1
    else:
        # теоретически не должны сюда попадать, проверяем на всякий
        raise HTTPException(status_code=400, detail=f"unknown scene: {scene}")

    now = datetime.now(timezone.utc)

    event = Event(
        ts=now,
        cycle=CORE.cycle,
        source=source,
        scene=scene,
        payload=payload or {},
    )

    # кладём новое событие в начало (новейшие сверху)
    CORE.events.insert(0, event)
    # ограничиваем историю таймлайна
    if len(CORE.events) > 200:
        CORE.events.pop()

    CORE.last_update = now
    return event


# --- входящая модель для /api/event ---

class EventIn(BaseModel):
    scene: Literal["intro", "reflect", "transition"]
    source: str = "ui"
    payload: dict[str, Any] | None = None


# --- публичные эндпоинты API ---

@router.get("/status")
async def api_status():
    """
    Текущее состояние ядра.
    Используется панелью наблюдения и /timeline.
    """
    return {"ok": True, "core": CORE}


@router.get("/timeline")
async def api_timeline(
    limit: int = Query(20, ge=1, le=200),
):
    """
    Лента событий (новые сверху).
    """
    return {
        "ok": True,
        "events": CORE.events[:limit],
    }


@router.post("/event")
async def api_event(
    body: EventIn,
    x_guard_key: str | None = Header(default=None, convert_underscores=False),
):
    """
    Production-эндпоинт для записи событий ядра.

    Правила:
    - Требует корректный X-Guard-Key (если GUARD_KEY задан в окружении).
    - scene ∈ {"intro","reflect","transition"}.
    - При "transition" увеличивает номер цикла (CORE.cycle).
    - Возвращает записанное событие и свежее состояние ядра.
    """
    _check_guard(x_guard_key)

    event = _push_event(
        scene=body.scene,
        source=body.source or "ui",
        payload=body.payload or {},
    )

    return {
        "ok": True,
        "event": event,
        "core": CORE,
    }
