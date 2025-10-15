# app/health.py
from __future__ import annotations
import asyncio
import logging
import os
import time
import aiohttp

log = logging.getLogger("health")

HEALTHCHECKS_URL = os.getenv("HEALTHCHECKS_URL", "").strip()
INTERVAL_SEC = int(os.getenv("HEALTHCHECKS_INTERVAL", "300"))       # 5 минут по умолчанию
STARTUP_GRACE = int(os.getenv("HEALTHCHECKS_STARTUP_GRACE", "10"))  # подождать после старта

_started = time.time()


async def _loop():
    """Фоновая петля для heartbeat-пингов в healthchecks.io (или совместимый URL)."""
    if not HEALTHCHECKS_URL:
        log.info("healthchecks: disabled (no HEALTHCHECKS_URL)")
        return

    await asyncio.sleep(STARTUP_GRACE)

    async with aiohttp.ClientSession() as sess:
        while True:
            try:
                async with sess.get(HEALTHCHECKS_URL, timeout=10) as r:
                    # Читаем тело, чтобы гарантировать закрытие соединения
                    await r.text()
                log.info("healthchecks: ping ok")
            except Exception as e:
                log.warning("healthchecks: ping failed: %r", e)
            await asyncio.sleep(INTERVAL_SEC)


def start(loop: asyncio.AbstractEventLoop) -> None:
    """Запуск фоновой задачи. Безопасно вызывать многократно — создаёт одну задачу."""
    loop.create_task(_loop())


def uptime_seconds() -> int:
    """Аптайм процесса с момента импорта/старта."""
    return int(time.time() - _started)
