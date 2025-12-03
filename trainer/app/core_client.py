from __future__ import annotations

import logging
from typing import Any, Dict, Optional

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

CORE_URL = settings.trainer_core_url.rstrip("/")
GUARD_KEY = settings.trainer_guard_key


async def send_timeline_event(
    scene: str,
    payload: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Асинхронная отправка события тренера в ядро Элайи (Stagecoach Web).
    """
    if not CORE_URL:
        logger.warning("Trainer core URL is not set; skip sending event %r", scene)
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
            resp = await client.post(url, json=data, headers=headers)
            resp.raise_for_status()
            logger.info("Trainer event sent: %s", scene)

    except httpx.HTTPStatusError as e:
        # Ключевая диагностическая строка: сразу видно статус, URL, заголовки и ответ ядра
        logger.error(
            "ERROR sending trainer event: %s %s headers=%r body=%r",
            e.response.status_code,
            e.request.url,
            headers,
            e.response.text,
        )
        raise
    except Exception as e:
        # Любая другая ошибка — логируем, но не роняем бота
        logger.error("ERROR sending trainer event %r: %s", scene, e)
