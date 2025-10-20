from __future__ import annotations
import asyncio
import logging
import os
from typing import Optional

import aiohttp

log = logging.getLogger("health")

def boot_health(*, env: str, release: str) -> None:
    log.info("Health boot: env=%s release=%s", env, release)

async def _ping(url: str) -> None:
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(url, timeout=10) as r:
                await r.text()
        log.info("Heartbeat OK: %s", url)
    except Exception as e:
        log.warning("Heartbeat FAIL: %s (%s)", url, e)

async def heartbeat_loop(url: str, interval_sec: int = 300, startup_grace: int = 10) -> None:
    await asyncio.sleep(max(0, startup_grace))
    while True:
        await _ping(url)
        await asyncio.sleep(max(30, interval_sec))

def start_heartbeat_if_configured(loop: asyncio.AbstractEventLoop) -> Optional[asyncio.Task]:
    url = (os.getenv("CRONITOR_PING_URL") or os.getenv("HEALTHCHECKS_URL") or "").strip()
    if not url:
        return None
    interval = int(os.getenv("HEALTHCHECKS_INTERVAL", "300") or "300")
    grace = int(os.getenv("HEALTHCHECKS_STARTUP_GRACE", "10") or "10")
    log.info("Heartbeat enabled: url=%s interval=%ss grace=%ss", url, interval, grace)
    return loop.create_task(heartbeat_loop(url, interval, grace))
