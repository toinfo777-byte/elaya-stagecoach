# trainer/app/core_client.py
from __future__ import annotations

import os
from typing import Any, Dict

import httpx

CORE_URL = os.getenv("TRAINER_CORE_URL", "").rstrip("/")
GUARD_KEY = os.getenv("TRAINER_GUARD_KEY", "").strip()


def _make_headers() -> Dict[str, str]:
    headers: Dict[str, str] = {}
    if GUARD_KEY:
        headers["X-Guard-Key"] = GUARD_KEY
    return headers


async def send_timeline_event(
    scene: str,
    payload: Dict[str, Any] | None = None,
) -> None:
    """
    Асинхронная отправка события тренера в ядро Элайи.
    """
    if not CORE_URL:
        print("WARN: TRAINER_CORE_URL not set")
        return

    url = f"{CORE_URL}/event" if CORE_URL.endswith("/api") else f"{CORE_URL}/api/event"

    data = {
        "source": "trainer",
        "scene": scene,
        "payload": payload or {},
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(url, json=data, headers=_make_headers())
            resp.raise_for_status()
            print("Trainer event sent:", scene)
    except Exception as exc:  # noqa: BLE001
        print("ERROR sending trainer event:", exc)
