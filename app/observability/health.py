from __future__ import annotations

import asyncio
import logging
import os

import aiohttp


async def _heartbeat_loop() -> None:
    """
    Пингуем Cronitor каждые 300 сек (5 мин).
    Если URL не задан — тихо выходим (без ошибок).
    """
    url = os.getenv("CRONITOR_URL") or os.getenv("HEALTHCHECKS_URL")
    if not url:
        logging.info("ℹ️ Cronitor heartbeat disabled (no CRONITOR_URL/HEALTHCHECKS_URL)")
        return

    interval = int(os.getenv("HEALTHCHECKS_INTERVAL", "300"))
    timeout = aiohttp.ClientTimeout(total=10)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        while True:
            try:
                async with session.get(url) as resp:
                    logging.info("💓 Cronitor beat: %s", resp.status)
            except Exception as e:
                logging.warning("⚠️ Cronitor heartbeat error: %s", e)
            await asyncio.sleep(interval)


def start_healthcheck():
    """
    Запускаем таску внутри текущего event loop.
    Возвращаем task только для логов/отладки.
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # на всякий случай—если вызвали слишком рано
        loop = asyncio.get_event_loop()

    task = loop.create_task(_heartbeat_loop(), name="cronitor-heartbeat")
    logging.info("✅ Cronitor heartbeat task started")
    return task
