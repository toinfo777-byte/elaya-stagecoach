# trainer/app/core_client.py
from __future__ import annotations

import logging
import os
from typing import Any, Dict

import httpx

logger = logging.getLogger(__name__)

# URL ядра (web-сервиса) и ключ защиты для тренера
WEB_URL = os.getenv("WEB_URL", "http://127.0.0.1:8000").rstrip("/")
TRAINER_GUARD_KEY = os.getenv("TRAINER_GUARD_KEY", "").strip()

logger.warning(
    "CORE_CLIENT init: WEB_URL=%r, TRAINER_GUARD_KEY=%r",
    WEB_URL,
    TRAINER_GUARD_KEY or "<empty>",
)


def _build_headers() -> Dict[str, str]:
    headers: Dict[str, str] = {}
    if TRAINER_GUARD_KEY:
        headers["X-Guard-Key"] = TRAINER_GUARD_KEY
    return headers


def _client() -> httpx.AsyncClient:
    return httpx.AsyncClient(base_url=WEB_URL, timeout=5.0)


# ---------------------------------------------------------------------------
#  ОТПРАВКА СОБЫТИЙ ТАЙМЛАЙНА
# ---------------------------------------------------------------------------


async def send_timeline_event(
    scene: str,
    payload: Dict[str, Any] | None = None,
) -> None:
    """
    Отправка события тренера в web-ядро (/api/event).
    """
    data = {
        "source": "trainer",
        "scene": scene,
        "payload": payload or {},
    }

    try:
        async with _client() as client:
            resp = await client.post(
                "/api/event",
                json=data,
                headers=_build_headers(),
            )
            resp.raise_for_status()
    except Exception:
        logger.exception("Failed to send trainer event %s", scene)
        raise


# ---------------------------------------------------------------------------
#  ЗАПРОС ПРОГРЕССА
# ---------------------------------------------------------------------------


async def fetch_progress(tg_user_id: int) -> Dict[str, Any]:
    """
    Запрос прогресса у web-ядра (/api/progress).
    """
    params = {"tg_user_id": tg_user_id}

    try:
        async with _client() as client:
            resp = await client.get(
                "/api/progress",
                params=params,
                headers=_build_headers(),
            )
            resp.raise_for_status()
            return resp.json()
    except Exception:
        logger.exception("Failed to fetch progress for user %s", tg_user_id)
        raise
