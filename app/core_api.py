import logging
from typing import Any, Dict

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


async def send_timeline_event(kind: str, payload: Dict[str, Any] | None = None) -> bool:
    """
    Отправка события в web-ядро Элайи (/api/timeline).

    Ошибки логируем, но НЕ ломаем работу бота.
    """
    base = settings.BASE_URL.rstrip("/")
    url = f"{base}/api/timeline"

    data = {
        "kind": kind,
        "payload": payload or {},
    }

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(url, json=data)
        resp.raise_for_status()
    except Exception as e:  # noqa: BLE001
        logger.warning("Failed to send timeline event %s: %s", kind, e)
        return False

    return True
