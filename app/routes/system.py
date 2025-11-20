from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

import os

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api", tags=["api"])

# --- защита (используем для мутирующих запросов, например /timeline, /sync) ---

GUARD_KEY = os.getenv("GUARD_KEY", "").strip()


def _check_guard(x_guard_key: str | None) -> None:
    """
    Простая защита для внутренних API.
    Если GUARD_KEY не задан — защита отключена.
    Если задан — требуем заголовок X-Guard-Key с тем же значением.
    """
    if not GUARD_KEY:
        return  # защита отключена

    if (x_guard_key or "").strip() != GUARD_KEY:
        raise HTTPException(status_code=401, detail="invalid guard key")


# --- ядро состояния: работаем через StateStore, если он есть; иначе — мягкий fallback ---

try:
    from app.core.state import StateStore  # type: ignore[attr-defined]
except Exception:
    StateStore = None  # type: ignore[assignment]


def _store_event(kind: str, payload: dict[str, Any]) -> None:
    """
    Унифицированная запись событий в StateStore (если он есть).
    Никаких исключений наверх не кидаем — агент не должен падать из-за ядра.
    """
    if not StateStore:
        return

    try:
        store = StateStore.get_instance()
        store.add_event(kind=kind, payload=payload)
    except Exception:
        # логирование можно добавить позже, сейчас просто не роняем API
        return


# --- /api/status — минимальный "пульс" ядра для CLI-агента ---


@router.get("/status")
async def api_status() -> dict[str, Any]:
    """
    Базовый статус ядра для CLI-агента и внутренних проверок.

    Используется elaya-cli (функция ping_core) для команды `elaya3 sync`.
    """
    now_utc = datetime.now(timezone.utc).isoformat()

    data: dict[str, Any] = {
        "status": "ok",
        "source": "elaya-core",
        "time": now_utc,
    }

    # Пытаемся обогатить ответ данными из StateStore (если он есть)
    if StateStore:
        try:
            store = StateStore.get_instance()
            data["state_ready"] = True
            # если у StateStore есть метод count_events — используем, иначе просто пропускаем
            if hasattr(store, "count_events"):
                data["timeline_len"] = store.count_events(kind="timeline")
        except Exception:
            data["state_ready"] = False

    return data


# --- /api/timeline — приём событий таймлайна от UI, ботов, CLI и т.п. ---


class TimelineEvent(BaseModel):
    channel: str = "cli"
    level: str = "info"
    message: str
    extra: Optional[dict[str, Any]] = None
    ts: Optional[str] = None


@router.post("/timeline")
async def api_timeline(
    event: TimelineEvent,
    x_guard_key: str | None = Header(default=None),
) -> dict[str, Any]:
    """
    Приём события таймлайна.
    Используется для внутреннего Pulse (UI, боты, CLI-агент и т.п.).
    Защищён GUARD_KEY, чтобы извне сюда нельзя было стучаться.
    """
    _check_guard(x_guard_key)

    payload = event.dict()
    if not payload.get("ts"):
        payload["ts"] = datetime.now(timezone.utc).isoformat()

    _store_event("timeline", payload)

    return {"ok": True}
