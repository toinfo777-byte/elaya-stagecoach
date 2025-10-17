# app/observability/health.py
import asyncio
import logging
import os
import aiohttp

async def _heartbeat_loop():
    url = os.getenv("CRONITOR_URL")
    if not url:
        logging.info("Cronitor heartbeat disabled (no CRONITOR_URL)")
        return
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    logging.info("💓 Cronitor beat: %s", resp.status)
        except Exception as e:
            logging.warning("⚠️ Cronitor heartbeat error: %s", e)
        await asyncio.sleep(300)  # 5 минут

def start_healthcheck():
    loop = asyncio.get_event_loop()
    task = loop.create_task(_heartbeat_loop())
    task.set_name("device-heartbeat")
    logging.info("✅ Cronitor heartbeat task started")
    return task
