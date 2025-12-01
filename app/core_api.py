# app/core_api.py
from __future__ import annotations

import httpx

from app.config import settings


async def send_timeline_event(scene: str, payload: dict | None = None) -> None:
    base = settings.base_url.rstrip("/")
    url = f"{base}/api/event"

    headers = {}
    if settings.guard_key:
        headers["X-Guard-Key"] = settings.guard_key

    data = {
        "source": "trainer-bot",
        "scene": scene,
        "payload": payload or {},
    }

    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.post(url, json=data, headers=headers)
        r.raise_for_status()


async def fetch_training_progress(user_id: int) -> dict:
    """
    Забираем прогресс из ядра (/api/progress).
    """
    base = settings.base_url.rstrip("/")
    url = f"{base}/api/progress"

    params = {"user_id": user_id}

    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(url, params=params)
        r.raise_for_status()
        return r.json()
