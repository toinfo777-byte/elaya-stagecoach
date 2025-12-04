# trainer/app/core_client.py
from __future__ import annotations

import os
from typing import Any, Dict, Optional

import httpx

CORE_URL = os.getenv("TRAINER_CORE_URL", "").rstrip("/")
GUARD_KEY = os.getenv("TRAINER_GUARD_KEY", "").strip()


async def send_timeline_event(scene: str, payload: Optional[Dict[str, Any]] = None) -> None:
    """
    Асинхронная отправка события тренера в ядро Элайи.
    """
    if not CORE_URL:
        print("WARN: TRAINER_CORE_URL not set")
        return

    url = f"{CORE_URL}/api/event"

    headers: Dict[str, str] = {}
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
    except httpx.RequestError as e:
        print(f"ERROR: failed to send trainer event {scene}: {e!r}")


async def fetch_progress(user_id: int, limit: int = 7) -> Dict[str, Any]:
    """
    Получить сводку прогресса пользователя из ядра.

    Ожидаемый ответ ядра (обобщённо):
    {
        "status": "ok",
        "user_id": 123,
        "total_days": 3,
        "last_date": {...} | {},
        "days": [{...}, ...]
    }
    """
    if not CORE_URL:
        print("WARN: TRAINER_CORE_URL not set")
        return {}

    url = f"{CORE_URL}/api/trainer/progress"

    params = {
        "user_id": user_id,
        "limit": limit,
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(url, params=params)
            r.raise_for_status()
            return r.json()
    except httpx.HTTPStatusError as e:
        print(f"ERROR: fetch_progress HTTP {e.response.status_code} for url={e.request.url}")
        return {}
    except httpx.RequestError as e:
        print(f"ERROR: fetch_progress request error {e!r}")
        return {}
