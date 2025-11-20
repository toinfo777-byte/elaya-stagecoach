# app/routes/system.py

from __future__ import annotations

import os
import threading
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Header, HTTPException

router = APIRouter(prefix="/api", tags=["api"])

# ----------------- защита (для мутаций) -----------------

GUARD_KEY = os.getenv("GUARD_KEY", "").strip()


def _check_guard(x_guard_key: Optional[str]) -> None:
    """
    Если GUARD_KEY не задан — защита выключена.
    Если задан — сверяем с заголовком X-Guard-Key, иначе 401.
    """
    if not GUARD_KEY:
        return

    if (x_guard_key or "").strip() != GUARD_KEY:
        raise HTTPException(status_code=401, detail="invalid guard key")


# ----------------- простое ядро состояния -----------------


class CoreState:
    """
    Минимальное состояние ядра Элайи в памяти процесса.

    Этого достаточно для:
    — счётчиков intro / reflect / transition
    — цикла обновлений
    — хранения последних событий для таймлайна.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.cycle: int = 0
        self.last_update: str = "-"
        self.intro: int = 0
        self.reflect: int = 0
        self.transition: int = 0
        self.events: List[Dict[str, Any]] = []
        self.reflection: Dict[str, Any] = {"text": "", "updated_at": "-"}

    def snapshot(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "cycle": self.cycle,
                "last_update": self.last_update,
                "intro": self.intro,
                "reflect": self.reflect,
                "transition": self.transition,
                "events": list(self.events),
                "reflection": dict(self.reflection),
            }

    def push_event(
        self,
        *,
        source: str,
        scene: str,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        ts = datetime.now(timezone.utc).isoformat()

        with self._lock:
            # обновляем цикл и счётчики сцен
            self.cycle += 1
            self.last_update = ts

            if scene == "intro":
                self.intro += 1
            elif scene == "reflect":
                self.reflect += 1
            elif scene == "transition":
                self.transition += 1

            event = {
                "ts": ts,
                "cycle": self.cycle,
                "source": source,
                "scene": scene,
                "payload": payload,
            }

            self.events.append(event)

        return event


STATE = CoreState()

# ----------------- healthcheck -----------------


@router.get("/healthz")
async def healthz() -> Dict[str, Any]:
    """
    Простой healthcheck для Render.
    """
    return {"ok": True}


# ----------------- status -----------------


@router.get("/status")
async def status() -> Dict[str, Any]:
    """
    Отдаём минимальное состояние ядра для HQ / dashboard.

    Формат:
    {
      "ok": true,
      "core": {
        "cycle": ...,
        "last_update": "...",
        "intro": ...,
        "reflect": ...,
        "transition": ...,
        "events": [...],
        "reflection": {...}
      }
    }
    """
    core = STATE.snapshot()
    return {"ok": True, "core": core}


# ----------------- приём событий от бота / UI -----------------


@router.post("/event")
async def event(
    body: Dict[str, Any],
    x_guard_key: Optional[str] = Header(default=None, alias="X-Guard-Key"),
) -> Dict[str, Any]:
    """
    Универсальная точка входа событий от бота / UI.

    Ожидаемый формат тела:
    {
      "source": "bot" | "ui" | "...",
      "scene": "start" | "intro" | "reflect" | "transition" | "...",
      "payload": { ... }    # любой JSON-словарь
    }
    """
    _check_guard(x_guard_key)

    source = str(body.get("source") or "unknown")
    scene = str(body.get("scene") or "unknown")
    raw_payload = body.get("payload") or {}

    if not isinstance(raw_payload, dict):
        payload: Dict[str, Any] = {"value": raw_payload}
    else:
        payload = raw_payload

    event = STATE.push_event(source=source, scene=scene, payload=payload)
    return {"ok": True, "event": event}


# ----------------- API для таймлайна -----------------


@router.get("/timeline")
async def api_timeline() -> Dict[str, Any]:
    """
    Лёгкий API для страницы /timeline.

    Страница ожидает:
    {
      "ok": true,
      "events": [ {ts, source, scene, payload, ...}, ... ]
    }
    """
    core = STATE.snapshot()
    return {"ok": True, "events": core["events"]}
