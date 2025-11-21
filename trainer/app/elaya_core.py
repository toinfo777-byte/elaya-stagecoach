from __future__ import annotations
import os
import httpx

CORE_URL = os.getenv("TRAINER_CORE_URL", "").rstrip("/")
GUARD_KEY = os.getenv("TRAINER_GUARD_KEY", "").strip()

async def send_timeline_event(scene: str, payload: dict | None = None) -> None:
    """
    Асинхронная отправка события тренера в ядро Элайи.
    """
    if not CORE_URL:
        print("WARN: TRAINER_CORE_URL not set")
        return

    url = f"{CORE_URL}/api/event"

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
            r = await client.post(url, json=data, headers=headers)
            r.raise_for_status()
            print("Trainer event sent:", scene)
    except Exception as exc:
        print("Trainer event error:", exc)
