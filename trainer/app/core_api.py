# trainer/app/core_api.py
from __future__ import annotations

import os
from typing import Any, Dict, Optional

import httpx

# Базовый URL ядра (elaya-stagecoach-web)
# Берём из нескольких переменных, чтобы не зависеть от конкретного имени
CORE_API_BASE = (
    os.getenv("CORE_API_BASE", "")
    or os.getenv("CORE_URL", "")
    or os.getenv("CORE_BASE_URL", "")
    or os.getenv("TRAINER_CORE_URL", "")
).rstrip("/")

# Путь для событий таймлайна (по умолчанию /api/timeline)
CORE_EVENTS_PATH = os.getenv("CORE_EVENTS_PATH", "/api/timeline")

# Ключ защиты (если на ядре GUARD выключен — можно оставить пустым)
GUARD_KEY = os.getenv("GUARD_KEY", "").strip()


async def send_timeline_event(
    scene: str,
    payload: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Асинхронная отправка события тренера в ядро Элайи.

    scene  — короткое имя сцены ("training_start", "training_done" и т.п.)
    payload — любые данные по событию (dict)
    """
    if not CORE_API_BASE:
        print("WARN: CORE_API_BASE is not set, timeline event skipped")
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
            print(f"[trainer→core] event sent: {scene} -> {url}")
    except Exception as exc:
        print(f"[trainer→core] event error: {exc} | URL={url}")
