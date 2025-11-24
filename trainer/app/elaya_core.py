from __future__ import annotations

import os
import httpx

# Базовый URL ядра Элайи
CORE_API_BASE = (
    os.getenv("CORE_API_BASE")
    or os.getenv("CORE_BASE_URL")
    or os.getenv("CORE_URL")
    or os.getenv("TRAINER_CORE_URL", "")
).rstrip("/")

# Путь для событий: по умолчанию /api/event
CORE_EVENTS_PATH = os.getenv("CORE_EVENTS_PATH", "/api/event")

# Ключ защиты (если GUARD включён на веб-сервисе)
GUARD_KEY = (
    os.getenv("GUARD_KEY", "").strip()
    or os.getenv("TRAINER_GUARD_KEY", "").strip()
)

async def send_timeline_event(scene: str, payload: dict | None = None) -> None:
    """
    Асинхронная отправка события тренера в ядро Элайи.
    """
    if not CORE_API_BASE:
        print("WARN: CORE_API_BASE (или TRAINER_CORE_URL) не задан")
        return

    url = f"{CORE_API_BASE}{CORE_EVENTS_PATH}"

    headers = {}
    if GUARD_KEY:
        headers["X-Guard-Key"] = GUARD_KEY

    data = {
        "source": "trainer",
        "scene": scene,
        "payload": payload or {},
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(url, json=data, headers=headers)
            resp.raise_for_status()
            print("Trainer event sent:", scene, "→", url)
    except Exception as exc:
        print("Trainer event error:", exc, "URL:", url)
