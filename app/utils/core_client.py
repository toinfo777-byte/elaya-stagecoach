from __future__ import annotations

import os
import logging

import httpx

logger = logging.getLogger(__name__)

CORE_BASE_URL = os.getenv("CORE_BASE_URL", "").rstrip("/")
CORE_EVENTS_PATH = os.getenv("CORE_EVENTS_PATH", "/api/event")


async def core_event(
    source: str,
    scene: str,
    payload: dict | None = None,
) -> None:
    """
    Отправка события в ядро.
    Если ядро недоступно / отвечает ошибкой, бот продолжает работать,
    мы просто логируем предупреждение.
    """
    if not CORE_BASE_URL:
        logger.info(
            "core_event: CORE_BASE_URL не задан, событие пропущено "
            "(source=%s, scene=%s)", source, scene
        )
        return

    url = f"{CORE_BASE_URL}{CORE_EVENTS_PATH}"
    data = {
        "source": source,
        "scene": scene,
        "payload": payload or {},
    }

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(url, json=data)
            if resp.status_code >= 400:
                # обрезаем HTML, чтобы не засорять логи
                text = resp.text[:200].replace("\n", " ")
                logger.warning(
                    "core_event: ядро ответило ошибкой %s: %s",
                    resp.status_code,
                    text,
                )
            else:
                logger.info("core_event: OK (%s %s)", source, scene)
    except Exception as e:
        logger.warning("core_event: запрос не удался: %r", e)
