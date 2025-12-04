# app/core_client.py
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

import httpx

from .config import settings

logger = logging.getLogger(__name__)

# URL ядра (Stagecoach Web), обрезаем хвостовой слэш на всякий случай
CORE_URL = (settings.trainer_core_url or "").rstrip("/")

# Ключ защиты, приводим к "чистому" виду
GUARD_KEY = (settings.trainer_guard_key or "").strip()


def _mask_secret(value: str) -> str:
    """
    Маскируем секреты в логах, чтобы случайно не светить ключи.
    """
    if not value:
        return ""
    if len(value) <= 4:
        return "***"
    return value[:2] + "***" + value[-2:]


async def send_timeline_event(
    scene: str,
    payload: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Асинхронная отправка события тренера в ядро Элайи (Stagecoach Web).

    ВАЖНО:
    - Любые ошибки логируем, но НЕ пробрасываем выше,
      чтобы тренер не ломал диалог с пользователем.
    - В логах не светим полный GUARD_KEY.
    """
    if not CORE_URL:
        logger.warning(
            "Trainer core URL is not set; skip event scene=%r", scene
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

        if resp.status_code >= 400:
            # Только диагностическая информация, без явного ключа
            logger.error(
                "Trainer event FAILED: scene=%s status=%s url=%s guard_set=%s body=%r",
                scene,
                resp.status_code,
                str(resp.url),
                bool(GUARD_KEY),
                resp.text[:200],  # обрежем, чтобы не раздувать лог
            )
            return

        logger.info(
            "Trainer event sent: scene=%s status=%s",
            scene,
            resp.status_code,
        )

    except Exception as e:
        logger.error(
            "Trainer event ERROR scene=%s: %s (core_url=%s, guard=%s)",
            scene,
            e,
            CORE_URL,
            _mask_secret(GUARD_KEY),
        )
        return
