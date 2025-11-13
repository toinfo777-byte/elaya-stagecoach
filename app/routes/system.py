from datetime import datetime, timezone
from typing import Any, Dict, Optional

import os
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api", tags=["api"])

# --- защита (только для мутаций) ---
GUARD_KEY = os.getenv("GUARD_KEY", "").strip()


def _check_guard(x_guard_key: str | None):
    if not GUARD_KEY:
        return  # защита отключена
    if (x_guard_key or "").strip() != GUARD_KEY:
        raise HTTPException(status_code=401, detail="invalid guard key")


# --- pydantic-модели ---

class SyncIn(BaseModel):
    """
    Расширенный sync:
    - source: от кого пришёл (ui/trainer/bot/...)
    - scene: intro/reflect/transition/...
    - payload: произвольная полезная нагрузка
    Все поля опциональны — для обратной совместимости.
    """
    source: Optional[str] = None
    scene: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None


class EventIn(BaseModel):
    """
    Входящее событие от тренера/бота.
    """
    source: str
    scene: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None


class ReflectionIn(BaseModel):
    text: str


# --- ядро ---


def _now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


try:
    from app.core.state import StateStore  # твой стор

    def _core_snapshot() -> Dict[str, Any]:
        return StateStore.get().get_state().snapshot()

    def _core_sync(
        source: str,
        scene: str | None = None,
        payload: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        store = StateStore.get()
        store.sync(source=source, scene=scene, payload=payload or {})
        return store.get_state().snapshot()

    def _core_add_event(
        source: str,
        scene: str | None = None,
        payload: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        store = StateStore.get()
        event = store.add_event(source=source, scene=scene, payload=payload or {})
        return event

    def _core_set_reflection(text: str) -> Dict[str, Any]:
        store = StateStore.get()
        reflection = store.set_reflection(text)
        # возвращаем полный снапшот ядра (включая обновлённую reflection)
        return store.get_state().snapshot()

except Exception:
    # fallback-ядро, если StateStore по какой-то причине не поднялся
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

    def _core_sync(
        source: str,
        scene: str | None = None,
        payload: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        CORE["cycle"] += 1
        now = _now_utc_iso()
        CORE["last_update"] = now
        event = {
            "ts": now,
            "cycle": CORE["cycle"],
            "source": source,
            "scene": scene or "transition",
            "payload": payload or {},
        }
        CORE.setdefault("events", [])
        CORE["events"].insert(0, event)
        CORE["events"] = CORE["events"][:50]
        return CORE

    def _core_add_event(
        source: str,
        scene: str | None = None,
        payload: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        now = _now_utc_iso()
        event = {
            "ts": now,
            "cycle": CORE.get("cycle", 0),
            "source": source,
            "scene": scene or "other",
            "payload": payload or {},
        }
        CORE.setdefault("events", [])
        CORE["events"].insert(0, event)
        CORE["events"] = CORE["events"][:50]
        return event

    def _core_set_reflection(text: str) -> Dict[str, Any]:
        now = _now_utc_iso()
        CORE.setdefault("reflection", {})
        CORE["reflection"]["text"] = text
        CORE["reflection"]["updated_at"] = now
        # фиксируем это как событие
        _core_add_event(
            source="reflection",
            scene="reflect",
            payload={"note": text},
        )
        return CORE


# --- endpoints ---


@router.get("/status")
async def api_status():
    """
    Минимальный снимок ядра:
    - cycle, last_update, counters
    - events[]
    - reflection
    """
    return {"ok": True, "core": _core_snapshot()}


@router.post("/sync")
async def api_sync(
    data: SyncIn | None = None,
    x_guard_key: str | None = Header(default=None, alias="X-Guard-Key"),
):
    """
    Инкремент цикла + запись события.
    Тело опционально — для обратной совместимости.
    """
    _check_guard(x_guard_key)

    source = (data.source if data and data.source else "ui")
    scene = data.scene if data else None
    payload = data.payload if data and data.payload is not None else {}

    core = _core_sync(source=source, scene=scene, payload=payload)
    return {"ok": True, "message": "synced", "core": core}


@router.post("/event")
async def api_event(
    data: EventIn,
    x_guard_key: str | None = Header(default=None, alias="X-Guard-Key"),
):
    """
    Безопасный вход событий от тренера/бота.
    НЕ инкрементит цикл — просто пишет событие в таймлайн.
    """
    _check_guard(x_guard_key)

    event = _core_add_event(
        source=data.source,
        scene=data.scene,
        payload=data.payload or {},
    )
    return {"ok": True, "event": event}


@router.get("/timeline")
async def api_timeline(limit: int = 50):
    """
    Публичный read-only таймлайн.
    Возвращает события в нормализованном виде:
    - ts
    - cycle
    - source
    - scene
    - payload
    """
    core = _core_snapshot()
    events = core.get("events", [])
    if not isinstance(events, list):
        events = []

    # events ожидаются в порядке "новое сверху"
    limit_norm = max(1, min(limit, 500))
    slice_events = events[:limit_norm]

    norm_events = []
    for e in slice_events:
        payload = e.get("payload") or {}
        norm_events.append(
            {
                "ts": e.get("ts"),
                "cycle": e.get("cycle", core.get("cycle", 0)),
                "source": e.get("source") or payload.get("source") or "system",
                "scene": e.get("scene") or e.get("kind") or "other",
                "payload": payload,
            }
        )

    return {"ok": True, "events": norm_events}


@router.post("/reflection")
async def api_reflection(
    data: ReflectionIn,
    x_guard_key: str | None = Header(default=None, alias="X-Guard-Key"),
):
    """
    Обновляет последнюю заметку (reflection) и пишет событие в таймлайн.
    """
    _check_guard(x_guard_key)
    core = _core_set_reflection(data.text)
    return {"ok": True, "reflection": core.get("reflection", {})}
