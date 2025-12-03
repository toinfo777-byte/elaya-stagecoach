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

    ВАЖНО: любые ошибки логируются, но НЕ пробрасываются выше,
    чтобы тренер не ломал диалог с пользователем.
    """
    if not CORE_URL:
        logger.warning("Trainer core URL is not set; skip event scene=%r", scene)
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

        # Если ядро ответило ошибкой — логируем и тихо выходим
        if resp.status_code >= 400:
            logger.error(
                "Trainer event FAILED: status=%s url=%s headers=%r body=%r",
                resp.status_code,
                resp.url,
                headers,
                resp.text,
            )
            return

        logger.info(
            "Trainer event sent: scene=%s status=%s",
            scene,
            resp.status_code,
        )

    except Exception as e:
        # Любая сетевая/другая ошибка — только лог
        logger.error("Trainer event ERROR scene=%s: %s", scene, e)
        return
