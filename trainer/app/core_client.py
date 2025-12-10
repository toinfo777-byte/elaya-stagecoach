# trainer/app/core_client.py
from __future__ import annotations

import logging
import os
from typing import Any, Dict, Optional

import httpx

logger = logging.getLogger(__name__)

# Базовый URL ядра (web-сервиса)
WEB_URL = os.getenv("WEB_URL", "http://127.0.0.1:8000").rstrip("/")

# Ключ защиты — берём либо специальный TRAINER_GUARD_KEY, либо общий GUARD_KEY
TRAINER_GUARD_KEY = (
    os.getenv("TRAINER_GUARD_KEY", "").strip()
    or os.getenv("GUARD_KEY", "").strip()
)


# ---------------------------------------------------------------------------
# 1. Отправка событий таймлайна
# ---------------------------------------------------------------------------

async def send_timeline_event(
    scene: str,
    payload: Optional[Dict[str, Any]] = None,
    source: str = "trainer",
) -> None:
    """
    Отправка события в ядро (web) на /api/event.

    :param scene: имя сцены, например "trainer.day.start"
    :param payload: произвольный JSON-словарь с данными
    :param source: источник события, по умолчанию "trainer"
    """
    if not WEB_URL:
        logger.warning("CORE_CLIENT: WEB_URL is not configured")
        return

    url = f"{WEB_URL}/api/event"

    headers: Dict[str, str] = {}
    if TRAINER_GUARD_KEY:
        headers["X-Guard-Key"] = TRAINER_GUARD_KEY

    data: Dict[str, Any] = {
        "source": source,
        "scene": scene,
        "payload": payload or {},
    }

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(url, json=data, headers=headers)
            resp.raise_for_status()
    except httpx.HTTPError as e:
        logger.error(
            "Failed to send trainer event %s: %s",
            scene,
            e,
        )


# ---------------------------------------------------------------------------
# 2. Получение прогресса для кнопки «📈 Мой прогресс»
# ---------------------------------------------------------------------------

async def fetch_progress(tg_user_id: int) -> Dict[str, Any]:
    """
    Запрашивает прогресс пользователя у ядра (web) через /api/progress.

    Ожидается ответ-словарь вида:
      {
        "total_days": int,
        "current_streak": int
      }

    Если что-то пошло не так — возвращает нули.
    """
    if not WEB_URL:
        logger.warning("CORE_CLIENT: WEB_URL is not configured")
        return {"total_days": 0, "current_streak": 0}

    url = f"{WEB_URL}/api/progress"

    headers: Dict[str, str] = {}
    if TRAINER_GUARD_KEY:
        headers["X-Guard-Key"] = TRAINER_GUARD_KEY

    params = {"tg_user_id": tg_user_id}

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(url, params=params, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            # Страховка на случай странного ответа
            return {
                "total_days": int(data.get("total_days", 0)),
                "current_streak": int(data.get("current_streak", 0)),
            }
    except httpx.HTTPError as e:
        logger.error("Failed to fetch progress for %s: %s", tg_user_id, e)
        return {"total_days": 0, "current_streak": 0}
