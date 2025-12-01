# trainer/app/core_api.py
from __future__ import annotations

import os
from typing import Any, Dict

import httpx

# --------------------------------------------------
# BACKWARD-COMPAT: константа CORE_URL для progress.py
# и других мест, где она уже импортируется.
# Ожидается TRAINER_CORE_URL БЕЗ /api.
# Пример: http://127.0.0.1:8000
# --------------------------------------------------
CORE_URL: str = os.getenv("TRAINER_CORE_URL", "").rstrip("/")


def _get_core_url() -> str:
    """
    Берём URL ядра из окружения. Если по какой-то причине
    новое значение не найдено, используем CORE_URL,
    прочитанный при импорте.
    """
    url = os.getenv("TRAINER_CORE_URL", "").rstrip("/")
    return url or CORE_URL


def _get_guard_key() -> str:
    """
    Берём GUARD-ключ тренера. Должен совпадать с GUARD_KEY ядра.
    """
    return os.getenv("TRAINER_GUARD_KEY", "").strip()


def _make_headers() -> Dict[str, str]:
    headers: Dict[str, str] = {}
    guard = _get_guard_key()
    if guard:
        headers["X-Guard-Key"] = guard
    return headers


async def send_timeline_event(
    scene: str,
    payload: Dict[str, Any] | None = None,
) -> None:
    """
    Асинхронная отправка события тренера в ядро Элайи.
    Используем POST /api/event с X-Guard-Key (если задан).
    """
    core_url = _get_core_url()
    if not core_url:
        print("WARN: TRAINER_CORE_URL not set — skip send_timeline_event")
        return

    url = f"{core_url}/api/event"

    data = {
        "source": "trainer",
        "scene": scene,
        "payload": payload or {},
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(url, json=data, headers=_make_headers())
            resp.raise_for_status()
            print("Trainer event sent:", scene)
    except Exception as exc:  # noqa: BLE001
        # не валим бота, просто логируем
        print("ERROR sending trainer event:", repr(exc))


async def safe_timeline(
    scene: str,
    payload: Dict[str, Any] | None = None,
) -> None:
    """
    Обёртка над send_timeline_event, которая никогда не роняет тренера.
    """
    try:
        await send_timeline_event(scene, payload)
    except Exception as exc:  # noqa: BLE001
        print("WARN: safe_timeline error:", repr(exc))
