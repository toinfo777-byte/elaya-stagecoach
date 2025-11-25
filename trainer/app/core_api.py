# trainer/app/core_api.py
from __future__ import annotations

import os
from typing import Any, Dict

import httpx

# базовый URL ядра (web-сервис)
CORE_API_BASE = os.getenv("CORE_API_BASE", "").rstrip("/")
# путь для событий; по умолчанию шлём в /api/timeline
CORE_EVENTS_PATH = os.getenv("CORE_EVENTS_PATH", "/api/timeline").strip()
if CORE_EVENTS_PATH and not CORE_EVENTS_PATH.startswith("/"):
    CORE_EVENTS_PATH = "/" + CORE_EVENTS_PATH

CORE_API_TOKEN = os.getenv("CORE_API_TOKEN", "").strip()
TRAINER_GUARD_KEY = os.getenv("TRAINER_GUARD_KEY", "").strip()
CORE_TIMEOUT = float(os.getenv("CORE_TIMEOUT", "5.0"))


async def send_timeline_event(scene: str, payload: Dict[str, Any]) -> None:
    """
    Отправка события в ядро (таймлайн Элайи).
    Никаких исключений наружу не выбрасываем — только логируем.
    """
    if not CORE_API_BASE:
        print(f"[trainer] CORE_API_BASE not set, skip timeline: scene={scene}, payload={payload}")
        return

    url = f"{CORE_API_BASE}{CORE_EVENTS_PATH}"
    data: Dict[str, Any] = {
        "source": "trainer",
        "scene": scene,
        "payload": payload or {},
    }

    headers: Dict[str, str] = {}
    if CORE_API_TOKEN:
        headers["Authorization"] = f"Bearer {CORE_API_TOKEN}"
    if TRAINER_GUARD_KEY:
        headers["X-Guard-Key"] = TRAINER_GUARD_KEY

    try:
        async with httpx.AsyncClient(timeout=CORE_TIMEOUT) as client:
            resp = await client.post(url, json=data, headers=headers)

        print(
            f"[trainer] timeline POST {url} -> {resp.status_code}, "
            f"scene={scene}, payload={payload}, resp={resp.text!r}"
        )
    except Exception as e:
        print(f"[trainer] timeline error: scene={scene}, payload={payload}, error={e!r}")
