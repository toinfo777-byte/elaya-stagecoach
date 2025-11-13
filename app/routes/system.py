from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

import os

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field, ValidationError

router = APIRouter(prefix="/api", tags=["api"])

# --- защита (только для мутаций) ---

GUARD_KEY = os.getenv("GUARD_KEY", "").strip()


def _check_guard(x_guard_key: str | None) -> None:
    """
    Если GUARD_KEY не задан — защита отключена.
    Если задан — любой POST/мутирующий запрос должен прийти с заголовком X-Guard-Key.
    """
    if not GUARD_KEY:
        return  # защита отключена
    if (x_guard_key or "").strip() != GUARD_KEY:
        raise HTTPException(status_code=401, detail="invalid guard key")


# --- ядро: работаем через StateStore, если он есть; иначе — минимальный CORE ---

try:
    # Если в проекте есть полноценный StateStore — используем его.
    from app.core.state import STATE  # type: ignore[attr-defined]
except Exception:  # noqa: BLE001
    # Фоллбек — простой in-memory core.
    class _MiniState:
        def __init__(self) -> None:
            self.core: dict[str, Any] = {
                "cycle": 0,
                "last_update": "-",
                "intro": 0,
                "reflect": 0,
                "transition": 0,
                "events": [],
                "reflection": {"text": "", "updated_at": "-"},
            }

        # Унифицированные методы для роутов
        def snapshot(self) -> dict[str, Any]:
            return self.core

        def set_core(self, core: dict[str, Any]) -> None:
            self.core = core

    STATE = _MiniState()  # type: ignore[assignment]


def _get_core() -> dict[str, Any]:
    """
    Аккуратно достаём core из STATE, поддерживая разные реализации StateStore.
    """
    state = STATE
    if hasattr(state, "snapshot"):
        return state.snapshot()  # type: ignore[no-any-return]
    if hasattr(state, "core"):
        return state.core  # type: ignore[no-any-return]
    # самый простой фоллбек
    return {
        "cycle": 0,
        "last_update": "-",
        "intro": 0,
        "reflect": 0,
        "transition": 0,
        "events": [],
        "reflection": {"text": "", "updated_at": "-"},
    }


def _set_core(core: dict[str, Any]) -> None:
    state = STATE
    if hasattr(state, "set_core"):
        state.set_core(core)
    elif hasattr(state, "core"):
        state.core = core  # type: ignore[attr-defined]


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


# --- Модели событий ---

SourceType = Literal["ui", "bot", "core"]
SceneType = Literal["intro", "reflect", "transition"]


class EventIn(BaseModel):
    source: SourceType = "ui"
    scene: SceneType
    payload: dict[str, Any] = Field(default_factory=dict)


class EventOut(BaseModel):
    ts: str
    cycle: int
    source: SourceType
    scene: SceneType
    payload: dict[str, Any]


# --- health / status ---

@router.get("/healthz")
async def healthz() -> dict[str, Any]:
    return {"ok": True}


@router.get("/status")
async def get_status() -> dict[str, Any]:
    core = _get_core()
    return {"ok": True, "core": core}


# --- НОВОЕ: публичный таймлайн для UI ---

@router.get("/timeline")
async def get_timeline() -> dict[str, Any]:
    """
    Публичный таймлайн для фронта.
    НЕ требует GUARD_KEY.
    Отдаёт только список событий.
    """
    core = _get_core()
    events: list[dict[str, Any]] = []
    if isinstance(core, dict):
        events = list(core.get("events", []))
    return {"ok": True, "events": events}


# --- production-версия /api/event ---

@router.post("/event")
async def post_event(
    body: dict[str, Any],
    x_guard_key: str | None = Header(default=None, convert_underscores=False),
) -> dict[str, Any]:
    """
    Принимаем событие от UI/бота/ядра, валидируем и сохраняем его в core.events.
    Пример тела запроса:
    {
      "source": "ui",
      "scene": "transition",
      "payload": { "note": "manual test from Talend" }
    }
    """

    # --- защита ---
    _check_guard(x_guard_key)

    # --- валидация входа ---
    try:
        event_in = EventIn.model_validate(body)
    except ValidationError as e:
        # Отдаём компактное описание ошибки валидации
        raise HTTPException(
            status_code=422,
            detail={"ok": False, "error": "invalid event schema", "details": e.errors()},
        ) from e

    # --- загружаем текущее состояние ---
    core = _get_core()

    # Гарантируем наличие нужных ключей в core (на случай старого состояния)
    core.setdefault("cycle", 0)
    core.setdefault("last_update", "-")
    core.setdefault("intro", 0)
    core.setdefault("reflect", 0)
    core.setdefault("transition", 0)
    core.setdefault("events", [])
    core.setdefault("reflection", {"text": "", "updated_at": "-"})

    # --- формируем новое событие ---
    next_cycle = int(core.get("cycle", 0)) + 1
    ts = _utc_now_iso()

    event_full = EventOut(
        ts=ts,
        cycle=next_cycle,
        source=event_in.source,
        scene=event_in.scene,
        payload=event_in.payload,
    ).model_dump()

    # --- обновляем core ---
    core["cycle"] = next_cycle
    core["last_update"] = ts

    # счётчики сцен
    if event_in.scene in ("intro", "reflect", "transition"):
        core[event_in.scene] = int(core.get(event_in.scene, 0)) + 1

    # список событий (держим только последние 20)
    events: list[dict[str, Any]] = list(core.get("events", []))
    events.append(event_full)
    if len(events) > 20:
        events = events[-20:]
    core["events"] = events

    # --- сохраняем состояние ---
    _set_core(core)

    return {"ok": True, "event": event_full}
