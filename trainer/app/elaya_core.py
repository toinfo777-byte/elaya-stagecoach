# trainer/app/elaya_core.py
from __future__ import annotations

import os
from typing import Any, Dict, Optional

import httpx

# базовый URL ядра (elaya-stagecoach-web)
CORE_API_BASE = (
    os.getenv("CORE_API_BASE", "")
    or os.getenv("TRAINER_CORE_URL", "")
).rstrip("/")

# путь для событий таймлайна (по умолчанию /api/timeline)
CORE_EVENTS_PATH = os.getenv("CORE_EVENTS_PATH", "/api/timeline")

# ключ защиты (можно использовать общий GUARD_KEY или отдельный TRAINER_GUARD_KEY)
GUARD_KEY = (
    os.getenv("GUARD_KEY", "").strip()
    or os.getenv("TRAINER_GUARD_KEY", "").strip()
)


async def send_timeline_event(scene: str, payload: Optional[Dict[str, Any]] = None) -> None:
    """
    Асинхронная отправка события тренера в ядро Элайи.
    """
    if not CORE_API_BASE:
        print("WARN: CORE_API_BASE (или TRAINER_CORE_URL) не задан, событие не отправлено")
        return

    url = f"{CORE_API_BASE}{CORE_EVENTS_PATH}"

    headers: Dict[str, str] = {}
    if GUARD_KEY:
        headers["X-Guard-Key"] = GUARD_KEY

    data: Dict[str, Any] = {
        "source": "trainer",
        "scene": scene,
        "payload": payload or {},
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(url, json=data, headers=headers)
            resp.raise_for_status()
            print("Trainer event sent:", scene, "->", url)
    except Exception as exc:
        print("Trainer event error:", exc, "URL:", url)
