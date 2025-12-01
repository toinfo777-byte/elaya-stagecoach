# cli/core_client.py
from __future__ import annotations

import os
from typing import Any, Dict

import httpx

# Ожидаем, что ELAYA_CORE_URL БЕЗ /api
# Пример: http://127.0.0.1:8000  или  https://elaya-stagecoach.onrender.com
CORE_URL = os.getenv("ELAYA_CORE_URL", "").rstrip("/")

# Тот же GUARD_KEY, что и в ядре
GUARD_KEY = os.getenv("GUARD_KEY", "").strip()


def _check_core_url() -> str:
    if not CORE_URL:
        raise RuntimeError("ELAYA_CORE_URL is not set")
    return CORE_URL


def _make_headers() -> Dict[str, str]:
    headers: Dict[str, str] = {}
    if GUARD_KEY:
        headers["X-Guard-Key"] = GUARD_KEY
    return headers


async def core_status() -> Dict[str, Any]:
    """
    GET /api/status — health-check ядра.
    GUARD_KEY не требуется.
    """
    base = _check_core_url()
    url = f"{base}/api/status"

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.json()


async def core_sync(client_payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    POST /api/sync — синхронизация состояния.
    ВСЕГДА с X-Guard-Key.
    """
    base = _check_core_url()
    url = f"{base}/api/sync"

    payload = {"client": client_payload}

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(url, json=payload, headers=_make_headers())
        resp.raise_for_status()
        return resp.json()


async def core_add_event(scene: str, payload: Dict[str, Any] | None = None) -> None:
    """
    POST /api/event — отправка события от CLI в таймлайн ядра.
    """
    base = _check_core_url()
    url = f"{base}/api/event"

    data = {
        "source": "cli",
        "scene": scene,
        "payload": payload or {},
    }

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(url, json=data, headers=_make_headers())
        resp.raise_for_status()
