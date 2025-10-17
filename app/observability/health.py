from __future__ import annotations
import asyncio
import logging
import os
from typing import Optional

import aiohttp

CRONITOR_OK: bool = False   # станет True, когда хотя бы один пинг ушёл успешно


async def _heartbeat_loop(url: str, interval: int, startup_grace: int) -> None:
    """Фоновая петля пинга Cronitor/Heartbeat."""
    global CRONITOR_OK
    # небольшая задержка на старт сервиса (инициализация бота и т.п.)
    if startup_grace > 0:
        await asyncio.sleep(startup_grace)

    timeout = aiohttp.ClientTimeout(total=min(interval - 1, 15))
    async with aiohttp.ClientSession(timeout=timeout) as session:
        while True:
            try:
                async with session.get(url) as resp:
                    if 200 <= resp.status < 300:
                        if not CRONITOR_OK:
                            logging.info("Healthcheck: first OK ping")
                        CRONITOR_OK = True
                    else:
                        logging.warning("Healthcheck: non-2xx: %s", resp.status)
            except Exception as e:
                logging.warning("Healthcheck ping error: %s", e)
            await asyncio.sleep(interval)


def start_healthcheck() -> Optional[asyncio.Task]:
    """
    Создаёт таску пинга ТОЛЬКО если есть URL. Вызывать ТОЛЬКО изнутри running loop.
    Возвращает Task или None (если URL не задан).
    """
    url = (os.getenv("HEALTHCHECKS_URL") or "").strip()
    if not url:
        logging.info("Healthcheck: URL not set — heartbeat disabled")
        return None

    try:
        interval = int(os.getenv("HEALTHCHECKS_INTERVAL", "300"))
    except ValueError:
        interval = 300
    try:
        startup_grace = int(os.getenv("HEALTHCHECKS_STARTUP_GRACE", "3"))
    except ValueError:
        startup_grace = 3

    task = asyncio.create_task(
        _heartbeat_loop(url, interval, startup_grace),
        name="cronitor-heartbeat",
    )
    return task
