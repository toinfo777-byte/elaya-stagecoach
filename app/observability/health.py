# app/observability/health.py
from __future__ import annotations

import os
import asyncio
import logging

import aiohttp

# URL пинга Cronitor/Healthchecks — возьмём из окружения
CRONITOR_URL = (os.getenv("HEALTHCHECKS_URL") or "").strip()
# Интервал между пингами (сек) — по умолчанию 300
PING_INTERVAL = int((os.getenv("HEALTHCHECK_INTERVAL") or "300").strip() or 300)


async def _ping_once() -> None:
    """
    Один пинг в Cronitor. Никаких исключений наружу — только логируем.
    """
    if not CRONITOR_URL:
        logging.warning("⚠️ Cronitor URL is not configured (HEALTHCHECKS_URL is empty).")
        return

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(CRONITOR_URL, timeout=10) as resp:
                if resp.status == 200:
                    logging.info("💓 Cronitor heartbeat sent successfully.")
                else:
                    logging.warning(f"⚠️ Cronitor heartbeat failed: HTTP {resp.status}")
    except asyncio.TimeoutError:
        logging.warning("⚠️ Cronitor heartbeat timeout.")
    except Exception as e:
        logging.warning(f"⚠️ Cronitor heartbeat error: {e}")


async def start_healthcheck() -> None:
    """
    Бесконечная задача: пингуем CRONITOR_URL каждые PING_INTERVAL секунд.
    Если URL не задан — тихо отключаемся.
    """
    if not CRONITOR_URL:
        logging.info("🩶 Healthcheck disabled (HEALTHCHECKS_URL is not set).")
        return

    logging.info(f"🩺 Healthcheck started: interval={PING_INTERVAL}s")
    while True:
        await _ping_once()
        await asyncio.sleep(PING_INTERVAL)
