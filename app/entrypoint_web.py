# app/entrypoint_web.py
from __future__ import annotations

import logging
import os

from fastapi import FastAPI, Request
import uvicorn

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Update

from app.routers import hq_status  # наш роутер команд
from app.config import settings  # если нет — замени прямым os.getenv

logger = logging.getLogger(__name__)
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))

# --- FastAPI + Aiogram
app = FastAPI(title="Elaya Stagecoach Web")

BOT_TOKEN = os.getenv("BOT_TOKEN") or os.getenv("TELEGRAM_TOKEN") or getattr(settings, "telegram_token", None)
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")

bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
dp.include_router(hq_status.router)  # подключаем команды

@app.on_event("startup")
async def on_startup():
    logger.info("Startup: webhook mode (Render)")
    # на Render мы работаем через webhook, polling НЕ запускаем

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.post("/tg/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.model_validate(data)
    await dp.feed_update(bot, update)
    return {"ok": True}

def main():
    port = int(os.getenv("PORT", "10000"))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")

if __name__ == "__main__":
    main()
