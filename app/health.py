# app/health.py
from __future__ import annotations
import asyncio
import logging
import os
import time
import aiohttp

log = logging.getLogger("health")

HEALTHCHECKS_URL = os.getenv("HEALTHCHECKS_URL", "").strip()   # пинквид из healthchecks.io
INTERVAL_SEC = int(os.getenv("HEALTHCHECKS_INTERVAL", "300"))  # по умолчанию 5 минут
STARTUP_GRACE = int(os.getenv("HEALTHCHECKS_STARTUP_GRACE", "10"))

_started = time.time()

async def _loop():
    if not HEALTHCHECKS_URL:
        log.info("healthchecks: disabled (no HEALTHCHECKS_URL)")
        return
    await asyncio.sleep(STARTUP_GRACE)
    async with aiohttp.ClientSession() as sess:
        while True:
            try:
                async with sess.get(HEALTHCHECKS_URL, timeout=10) as r:
                    await r.text()
                log.info("healthchecks: ping ok")
            except Exception as e:
                log.warning("healthchecks: ping failed: %r", e)
            await asyncio.sleep(INTERVAL_SEC)

def start(loop: asyncio.AbstractEventLoop):
    loop.create_task(_loop())

def uptime_seconds() -> int:
    return int(time.time() - _started)
