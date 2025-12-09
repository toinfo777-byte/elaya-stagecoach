# trainer/app/core_client.py
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

# Берём адрес ядра и guard-ключ из Settings
CORE_URL = (settings.trainer_core_url or "").rstrip("/")
GUARD_KEY = settings.trainer_guard_key or ""


async def send_timeline_event(scene: str, payload: Optional[Dict[str, Any]] = None) -> None:
    """
    Асинхронная отправка события тренера в ядро Элайи.
    """
    if not CORE_URL:
        logger.warning("TRAINER_CORE_URL not set — skip send_timeline_event(%s)", scene)
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
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.post(url, json=data, headers=headers)
            r.raise_for_status()
            logger.info("Trainer event sent: %s", scene)
    except Exception as e:  # noqa: BLE001
        logger.exception("Failed to send trainer event %s: %s", scene, e)


async def fetch_progress(user_id: int, limit: int = 7) -> Dict[str, Any]:
    """
    Временная заглушка для кнопки «Мой прогресс».
    Потом здесь будет запрос в ядро (Stagecoach Web).
    """
    # Минимальный набор данных, с которым форматтер прогресса точно не сломается.
    return {
        "user_id": user_id,
        "total_days": 0,
        "completed_days": 0,
        "recent_days": [],
    }
