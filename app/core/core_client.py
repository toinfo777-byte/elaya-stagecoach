# app/core/core_client.py

from __future__ import annotations

import os
from typing import Any, Dict, Optional

import httpx

CORE_BASE_URL = os.getenv("CORE_BASE_URL", "").rstrip("/")
CORE_TIMEOUT = float(os.getenv("CORE_TIMEOUT", "3.0"))
CORE_GUARD_KEY = os.getenv("CORE_GUARD_KEY", "").strip()


async def push_event(
    scene: str,
    payload: Optional[Dict[str, Any]] = None,
    source: str = "bot",
) -> None:
    """
    Отправляет событие в ядро StageCoach-web.

    scene: 'intro' | 'reflect' | 'transition'
    source: обычно 'bot'
    payload: любая служебная инфа (user_id, stage, текст и т.п.)
    """
    if not CORE_BASE_URL:
        # ядро не сконфигурировано — молча выходим, чтобы не ломать бота
        return

    data: Dict[str, Any] = {
        "source": source,
        "scene": scene,
        "payload": payload or {},
    }

    headers = {"Content-Type": "application/json"}
    if CORE_GUARD_KEY:
        # сейчас у тебя GUARD_KEY пустой → этот заголовок просто не уйдёт
        headers["X-Guard-Key"] = CORE_GUARD_KEY

    try:
        async with httpx.AsyncClient(timeout=CORE_TIMEOUT) as client:
            resp = await client.post(f"{CORE_BASE_URL}/api/event", json=data, headers=headers)
            resp.raise_for_status()
    except Exception:
        # В проде сюда можно повесить логгер, но бот не должен падать из-за ядра
        return
