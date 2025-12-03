from __future__ import annotations

import logging
import os
from typing import Any, Dict, Optional

import httpx

# URL ядра (web-сервис)
CORE_URL = os.getenv("TRAINER_CORE_URL", "").rstrip("/")
# Ключ для GUARD'а на стороне web
GUARD_KEY = os.getenv("TRAINER_GUARD_KEY", "").strip()


async def send_timeline_event(scene: str, payload: Optional[Dict[str, Any]] = None) -> None:
    """
    Асинхронная отправка события тренера в ядро Элайи.

    scene  — название сцены/шагa тренировки
    payload — произвольные данные по событию
    """
    if not CORE_URL:
        logging.warning(
            "TRAINER_CORE_URL is not set; skip sending event %r", scene
        )
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
        logging.info("Trainer event sent: %s", scene)
    except httpx.HTTPStatusError as e:
        # Ключевая диагностическая строка:
        logging.error(
            "ERROR sending trainer event: %s %s headers=%r body=%r",
            e.response.status_code,
            e.request.url,
            headers,
            e.response.text,
        )
        # пробрасываем, чтобы в логах явно был stacktrace HTTPStatusError
        raise
    except Exception as e:
        # Любая другая ошибка — логируем, но не роняем бота
        logging.error("ERROR sending trainer event %r: %s", scene, e)
