# app/utils/core_client.py

from __future__ import annotations

import logging
import os
from typing import Any, Dict, Optional

import httpx

logger = logging.getLogger(__name__)

# базовый URL ядра (web-сервис Stagecoach)
CORE_BASE_URL = (
    os.getenv("CORE_BASE_URL")
    or os.getenv("CORE_API_BASE")
    or os.getenv("STAGECOACH_WEB_URL")
    or ""
).rstrip("/")

CORE_API_TOKEN = os.getenv("CORE_API_TOKEN", "").strip()
CORE_GUARD_KEY = os.getenv("CORE_GUARD_KEY", "").strip()

try:
    CORE_TIMEOUT = float(os.getenv("CORE_TIMEOUT", "3.0"))
except ValueError:
    CORE_TIMEOUT = 3.0


async def core_event(
    *,
    source: str,
    scene: str,
    payload: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Отправка события в ядро Элайи (web-сервис) — /api/event.

    Никаких исключений наружу не выбрасываем:
    если ядро недоступно, бот продолжает работать как обычно.
    """
    if not CORE_BASE_URL:
        logger.info("core_event: CORE_BASE_URL не задан, пропускаю отправку события")
        return

    url = f"{CORE_BASE_URL}/api/event"
    payload = payload or {}

    headers: Dict[str, str] = {
        "Content-Type": "application/json",
    }

    if CORE_API_TOKEN:
        headers["Authorization"] = f"Bearer {CORE_API_TOKEN}"

    if CORE_GUARD_KEY:
        headers["X-Guard-Key"] = CORE_GUARD_KEY

    data = {
        "source": source,
        "scene": scene,
        "payload": payload,
    }

    try:
        async with httpx.AsyncClient(timeout=CORE_TIMEOUT) as client:
            resp = await client.post(url, json=data, headers=headers)
    except Exception as e:
        logger.warning("core_event: ошибка отправки в ядро: %r", e)
        return

    if resp.status_code >= 400:
        logger.warning(
            "core_event: ядро ответило ошибкой %s: %s",
            resp.status_code,
            resp.text[:200],
        )
    else:
        logger.debug("core_event: ok (%s)", resp.text[:200])
