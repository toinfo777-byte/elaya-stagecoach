from __future__ import annotations

import asyncio
import logging
import os

import aiohttp


async def _heartbeat_loop(url: str, interval: int, startup_grace: int) -> None:
    # даём сервису стартануть
    await asyncio.sleep(startup_grace)

    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(url, timeout=10) as resp:
                    logging.info("Cronitor heartbeat -> %s (status=%s)", url, resp.status)
            except Exception as e:
                logging.warning("Cronitor heartbeat failed: %s", e)
            await asyncio.sleep(interval)


def start_healthcheck() -> asyncio.Task | None:
    """
    Запускает heartbeat-таску ТОЛЬКО если уже есть running loop.
    Возвращает Task или None (если URL пустой или цикла ещё нет).
    """
    url = (os.getenv("HEALTHCHECKS_URL") or "").strip()
    if not url:
        logging.info("Cronitor: URL пустой — пульс отключён.")
        return None

    interval = int(os.getenv("HEALTHCHECKS_INTERVAL", "300") or 300)
    startup_grace = int(os.getenv("HEALTHCHECKS_STARTUP_GRACE", "15") or 15)

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # вызывать только из running loop — поэтому спокойно пропускаем
        logging.debug("Cronitor: нет running loop — heartbeat пока не запускаем.")
        return None

    task = loop.create_task(
        _heartbeat_loop(url, interval, startup_grace),
        name="cronitor-heartbeat",
    )
    return task
