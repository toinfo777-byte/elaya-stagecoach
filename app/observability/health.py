# app/observability/health.py
from __future__ import annotations
import asyncio
import logging
import os
from typing import Optional

import aiohttp

CRONITOR_OK: bool = False
LAST_PING_AT: Optional[float] = None


async def _heartbeat_loop(url: str, interval: int, startup_grace: int) -> None:
    """
    Бесконечный цикл пингов в Cronitor/heartbeat URL.
    Формат URL — готовый линк из Cronitor (Beat → Ping URL).
    """
    global CRONITOR_OK, LAST_PING_AT
    await asyncio.sleep(max(0, startup_grace))
    logging.info("Heartbeat loop started (interval=%ss, grace=%ss)", interval, startup_grace)

    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
        while True:
            try:
                async with session.get(url) as resp:
                    CRONITOR_OK = resp.status < 400
                    LAST_PING_AT = asyncio.get_event_loop().time()
                    if not CRONITOR_OK:
                        logging.warning("Heartbeat ping non-OK status: %s", resp.status)
            except Exception as e:
                CRONITOR_OK = False
                logging.warning("Heartbeat ping failed: %s", e)

            await asyncio.sleep(max(5, interval))


def start_healthcheck() -> Optional[asyncio.Task]:
    """
    Запускает heartbeat ТОЛЬКО если уже есть running loop (вызывается из main()).
    Возвращает Task или None.
    Переменные окружения:
      - HEALTHCHECKS_URL (обязателен для запуска)
      - HEALTHCHECKS_INTERVAL (сек, по умолчанию 300)
      - HEALTHCHECKS_STARTUP_GRACE (сек, по умолчанию 10)
    """
    url = (os.getenv("HEALTHCHECKS_URL") or "").strip()
    if not url:
        logging.info("Heartbeat disabled: HEALTHCHECKS_URL is empty")
        return None

    interval = int(os.getenv("HEALTHCHECKS_INTERVAL", "300") or 300)
    grace = int(os.getenv("HEALTHCHECKS_STARTUP_GRACE", "10") or 10)

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # вызывают до запуска цикла — не падаем, просто лог
        logging.warning("Heartbeat NOT started: no running event loop")
        return None

    task = loop.create_task(_heartbeat_loop(url, interval, grace), name="cronitor-heartbeat")
    return task
