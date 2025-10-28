from __future__ import annotations
import asyncio
import logging
from fastapi import FastAPI
from app.config import settings

app = FastAPI(title="Elaya Stagecoach")

@app.get("/health")
def health():
    return {"ok": True, "mode": settings.MODE}

# --- режим WEB: только Uvicorn поднимет app ---
if settings.MODE == "web":
    # НИКАКИХ импортов aiogram здесь!
    # Всё, что связано с ботом, подключаем только в режиме polling.
    logging.getLogger(__name__).info("Starting in WEB mode. Bot is disabled.")

# --- режим POLLING: отдельная корутина ---
async def run_polling():
    # импорт внутри, чтобы в web-режиме не тащить aiogram вообще
    from aiogram import Bot, Dispatcher
    from aiogram.client.default import DefaultBotProperties
    from aiogram.enums import ParseMode

    if not settings.BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is empty in polling mode")

    bot = Bot(token=settings.BOT_TOKEN,
              default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    # safety: чистим webhook перед polling
    try:
        await bot.delete_webhook(drop_pending_updates=True)
    except Exception as e:
        logging.warning("delete_webhook failed: %r", e)

    # тут подключаем роутеры бота (импорты тоже входят ТОЛЬКО в polling ветку)
    # from app.routers import ...
    # dp.include_router(...)

    logging.getLogger(__name__).info("Start polling")
    await dp.start_polling(bot)

if __name__ == "__main__":  # если запускается как скрипт
    if settings.MODE == "polling":
        asyncio.run(run_polling())
