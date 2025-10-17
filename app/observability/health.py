from __future__ import annotations
import asyncio
import logging
import os
from typing import Optional

import aiohttp

from .diag_status import mark_cronitor_ok

HEALTH_URL_ENV = "HEALTHCHECKS_URL"
INTERVAL_ENV = "HEALTHCHECKS_INTERVAL"
STARTUP_GRACE_ENV = "HEALTHCHECKS_STARTUP_GRACE"

async def _post_ping(session: aiohttp.ClientSession, url: str) -> None:
    async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
        if resp.status < 400:
            logging.info("Cronitor heartbeat OK (%s)", resp.status)
            mark_cronitor_ok()
        else:
            logging.warning("Cronitor heartbeat BAD (%s)", resp.status)

async def _heartbeat_loop(url: str, interval: int, startup_grace: int) -> None:
    await asyncio.sleep(max(0, startup_grace))
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                await _post_ping(session, url)
            except Exception as e:
                logging.warning("Cronitor ping error: %s", e)
            await asyncio.sleep(max(5, interval))

def start_healthcheck() -> Optional[asyncio.Task]:
    """
    Стартуем только когда уже есть running event loop (вызывается из main()).
    Возвращает Task или None, если URL не задан.
    """
    url = os.getenv(HEALTH_URL_ENV, "").strip()
    if not url:
        logging.info("Cronitor URL is empty — skip heartbeat.")
        return None

    interval = int(os.getenv(INTERVAL_ENV, "300"))
    startup_grace = int(os.getenv(STARTUP_GRACE_ENV, "5"))
    task = asyncio.create_task(
        _heartbeat_loop(url, interval, startup_grace),
        name="cronitor-heartbeat",
    )
    return task
