# app/routes/system.py
from typing import Any, Dict

from fastapi import APIRouter, Header
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import os

router = APIRouter(prefix="/api", tags=["api"])

# --- защита (временно мягкая: на web не блокируем) ---
GUARD_KEY = os.getenv("GUARD_KEY", "").strip()


def _check_guard(x_guard_key: str | None):
    """
    ВРЕМЕННО: защита выключена (no-op).
    Позже можно вернуть проверку для боевого тренера/бота.
    """
    return  # no-op


# --- ядро: работаем через StateStore, если он есть; иначе — fallback ---


try:
    from app.core.state import StateStore  # твой стор

    def _core_snapshot() -> Dict[str, Any]:
        return StateStore.get().get_state().snapshot()

    def _core_sync(source: str) -> Dict[str, Any]:
        StateStore.get().sync(source=source)
        return StateStore.get().get_state().snapshot()

    def _core_add_event(source: str, scene: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        StateStore.get().add_event(source=source, scene=scene, payload=payload)
        return StateStore.get().get_state().snapshot()

except Exception:
    # резервный режим без StateStore
    CORE: Dict[str, Any] = {
        "cycle": 0,
        "last_update": "-",
        "intro": 0,
        "reflect": 0,
        "transition": 0,
        "events": [],
        "reflection": {"text": "", "updated_at": "-"},
    }

    def _core_snapshot() -> Dict[str, Any]:
        return CORE

    def _core_sync(source: str) -> Dict[str, Any]:
        CORE["cycle"] += 1
        CORE["last_update"] = datetime.now(timezone.utc).isoformat()
        # минимальная модель события
        evt = {
            "ts": CORE["last_update"],
            "cycle": CORE["cycle"],
            "source": source,
            "scene": "transition",
            "payload": {},
        }
        CORE.setdefault("events", [])
        CORE["events"].insert(0, evt)
        CORE["events"] = CORE["events"][:200]
        return CORE

    def _core_add_event(source: str, scene: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        CORE["cycle"] += 1
        CORE["last_update"] = datetime.now(timezone.utc).isoformat()
        evt = {
            "ts": CORE["last_update"],
            "cycle": CORE["cycle"],
            "source": source,
            "scene": scene,
            "payload": payload or {},
        }
        CORE.setdefault("events", [])
        CORE["events"].insert(0, evt)
        CORE["events"] = CORE["events"][:200]
        return CORE


# --- схемы для входящих данных ---


class EventIn(BaseModel):
    """
    Минимальный контракт для тренера/бота.

    Пример JSON:
    {
      "source": "trainer",
      "scene": "intro",
      "payload": {
        "note": "пользователь зашёл в сцену intro",
        "user_id": 12345
      }
    }
    """

    source: str = Field(..., description="источник события: trainer | bot | ui | system")
    scene: str = Field(..., description="сцена/фаза портала: intro | reflect | transition | trainer | bot | ...")
    payload: Dict[str, Any] = Field(default_factory=dict, description="произвольный JSON-пакет")


# --- endpoints ---


@router.get("/status")
async def api_status():
    """Мини-снимок состояния ядра."""
    return {"ok": True, "core": _core_snapshot()}


@router.post("/sync")
async def api_sync(
    x_guard_key: str | None = Header(default=None, alias="X-Guard-Key"),
):
    """
    Ручная синхронизация ядра из UI.
    Сейчас использует сцену 'transition' и источник 'ui'.
    """
    _check_guard(x_guard_key)
    core = _core_sync(source="ui")
    return {"ok": True, "message": "synced", "core": core}


@router.get("/timeline")
async def api_timeline(limit: int = 50):
    """
    Публичный read-only таймлайн.
    Возвращает последние `limit` событий (max 500).
    """
    events = _core_snapshot().get("events", [])
    if not isinstance(events, list):
        events = []

    limit = max(1, min(limit, 500))
    return {"ok": True, "events": events[:limit]}


@router.post("/reflection")
async def api_reflection(
    text: str,
    x_guard_key: str | None = Header(default=None, alias="X-Guard-Key"),
):
    """
    Запись последней заметки (reflection).
    Сейчас тоже не проверяет ключ — soft-mode.
    """
    _check_guard(x_guard_key)
    core = _core_snapshot()
    core.setdefault("reflection", {})
    core["reflection"]["text"] = text
    core["reflection"]["updated_at"] = datetime.now(timezone.utc).isoformat()
    _core_sync(source="reflection")
    return {"ok": True, "reflection": core["reflection"]}


@router.post("/event")
async def api_event(
    event: EventIn,
    x_guard_key: str | None = Header(default=None, alias="X-Guard-Key"),
):
    """
    Приём произвольного события от тренера/бота.

    Использование (пример):
    POST /api/event
    {
      "source": "trainer",
      "scene": "intro",
      "payload": {
        "note": "intro started",
        "user_id": 123
      }
    }
    """
    _check_guard(x_guard_key)
    core = _core_add_event(
        source=event.source,
        scene=event.scene,
        payload=event.payload,
    )
    events = core.get("events", []) or []
    last = events[0] if events else None
    return {"ok": True, "event": last, "core": core}
