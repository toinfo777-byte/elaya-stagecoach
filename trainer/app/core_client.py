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

    ВАЖНО: любые ошибки сети или 5xx от ядра
    НЕ должны ломать обработку апдейта в боте.
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
            # здесь могут прилететь 5xx / 4xx
            r.raise_for_status()
            print("Trainer event sent:", scene)
    except httpx.HTTPStatusError as e:
        # ядро ответило, но с ошибкой (например, 500, 502, 503)
        print(
            f"ERROR: send_timeline_event HTTP {e.response.status_code} "
            f"for url={e.request.url}, scene={scene}"
        )
        # НЕ пробрасываем исключение дальше
    except httpx.RequestError as e:
        # проблемы сети, DNS, таймаут и т.п.
        print(f"ERROR: send_timeline_event request error for scene={scene}: {e!r}")
        # тоже просто логируем, бот продолжает жить


async def fetch_progress(user_id: int, limit: int = 7) -> Dict[str, Any]:
    """
    Получить сводку прогресса пользователя из ядра.

    Ожидаемый ответ ядра (обобщённо):
    {
        "user_id": 123,
        "total_days": 3,
        "current_streak": 2,
        "last_date": "2025-12-05"
    }
    """
    if not CORE_URL:
        print("WARN: TRAINER_CORE_URL not set")
        return {}

    url = f"{CORE_URL}/api/progress"

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
