from __future__ import annotations

import asyncio
import logging
import os
from typing import Any, Dict, Optional

import httpx

logger = logging.getLogger(__name__)

DEFAULT_WEB_URL = "http://127.0.0.1:8000"


def _web_url() -> str:
    return (os.getenv("WEB_URL") or DEFAULT_WEB_URL).rstrip("/")


def _guard_key() -> str:
    # ВАЖНО: у тебя именно TRAINER_GUARD_KEY (не GUARD_KEY)
    return (os.getenv("TRAINER_GUARD_KEY") or "").strip()


def _headers() -> Dict[str, str]:
    hk = _guard_key()
    # если ключ пустой — защита выключена на WEB, либо ты тестишь без неё
    return {"X-Guard-Key": hk} if hk else {}


def _timeout() -> httpx.Timeout:
    # Чтобы бот НЕ ВИСЕЛ по 5 сек при недоступном web:
    # connect/read/write/pool — короткие
    return httpx.Timeout(connect=0.6, read=0.8, write=0.8, pool=0.6)


async def _post(url: str, body: Dict[str, Any]) -> None:
    async with httpx.AsyncClient(timeout=_timeout()) as client:
        r = await client.post(url, json=body, headers=_headers())
        r.raise_for_status()


async def _get_json(url: str, params: Dict[str, Any]) -> Dict[str, Any]:
    async with httpx.AsyncClient(timeout=_timeout()) as client:
        r = await client.get(url, params=params, headers=_headers())
        r.raise_for_status()
        data = r.json()
        return data if isinstance(data, dict) else {}


def fire_and_forget(coro) -> None:
    # Никаких await — чтобы не было лага в ответе бота
    async def runner():
        try:
            await coro
        except Exception as e:
            logger.warning("core_client background task failed: %s", e)

    asyncio.create_task(runner())


async def send_timeline_event(scene: str, payload: Optional[Dict[str, Any]] = None) -> None:
    url = f"{_web_url()}/api/event"
    body = {"source": "trainer", "scene": scene, "payload": payload or {}}
    await _post(url, body)


async def fetch_progress(tg_user_id: int) -> Dict[str, Any]:
    url = f"{_web_url()}/api/progress"
    params = {"tg_user_id": tg_user_id}
    try:
        return await _get_json(url, params=params)
    except Exception as e:
        logger.warning("Failed to fetch progress: %s", e)
        return {"total_days": 0, "current_streak": 0}
