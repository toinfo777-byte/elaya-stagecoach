from __future__ import annotations

import asyncio
import logging
import os
from contextlib import asynccontextmanager

import aiohttp

from .diag_status import mark_cronitor_ok


@asynccontextmanager
async def _session():
    timeout = aiohttp.ClientTimeout(total=15)
    async with aiohttp.ClientSession(timeout=timeout) as s:
        yield s


async def _beat(url: str) -> bool:
    try:
        async with _session() as s:
            # Cronitor heartbeat — достаточно GET
            async with s.get(url) as resp:
                ok = 200 <= resp.status < 300
                if not ok:
                    logging.warning("Cronitor heartbeat HTTP %s", resp.status)
                return ok
    except Exception as e:
        logging.warning("Cronitor heartbeat failed: %s", e)
        return False


async def _heartbeat_loop(url: str, interval: int, startup_grace: int) -> None:
    if startup_grace > 0:
        await asyncio.sleep(startup_grace)

    while True:
        ok = await _beat(url)
        mark_cronitor_ok(ok)
        await asyncio.sleep(max(30, interval))  # страхуемся от слишком малого интервала


def start_healthcheck() -> asyncio.Task | None:
    """
    Стартует фоновый пульс Cronitor, если настроены переменные окружения.
    Возвращает Task, либо None.
    """
    url = (os.getenv("HEALTHCHECKS_URL") or "").strip()
    if not url:
        logging.info("Cronitor: URL not set — heartbeat disabled")
        mark_cronitor_ok(False)
        return None

    try:
        interval = int(os.getenv("HEALTHCHECKS_INTERVAL", "300"))
    except ValueError:
        interval = 300

    try:
        startup_grace = int(os.getenv("HEALTHCHECKS_STARTUP_GRACE", "5"))
    except ValueError:
        startup_grace = 5

    logging.info("Cronitor: heartbeat every %ss (startup_grace=%s)", interval, startup_grace)
    task = asyncio.create_task(_heartbeat_loop(url, interval, startup_grace), name="cronitor-heartbeat")
    return task
