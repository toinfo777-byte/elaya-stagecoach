from __future__ import annotations

import logging
import os

from fastapi import FastAPI
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Update

import sentry_sdk


# -----------------------------
#  Sentry (если настроен)
# -----------------------------
SENTRY_DSN = os.getenv("SENTRY_DSN")
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        environment=os.getenv("SENTRY_ENVIRONMENT", "trainer-bot"),
        traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.0")),
    )

# -----------------------------
#  Логирование
# -----------------------------
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)

logger = logging.getLogger("elaya-trainer-bot")

# -----------------------------
#  Bot & Dispatcher
# -----------------------------
BOT_TOKEN = os.getenv("BOT_TOKEN") or os.getenv("TELEGRAM_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN / TELEGRAM_TOKEN is not set in environment")

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
dp = Dispatcher()

# Роутеры бота
from app.routers.start import router as start_router  # noqa: E402

dp.include_router(start_router)

# -----------------------------
#  FastAPI-приложение
# -----------------------------
app = FastAPI(title="Elaya Trainer Bot")


@app.get("/")
async def root():
    """Проверочный эндпоинт для Render."""
    return {
        "ok": True,
        "service": "elaya-trainer-bot",
        "mode": "webhook",
    }


@app.get("/healthz")
async def healthz():
    """Healthcheck для Render."""
    return {"ok": True}


async def _process_update(data: dict) -> dict:
    """Общий обработчик апдейта Telegram."""
    update = Update.model_validate(data)
    await dp.feed_update(bot=bot, update=update)
    return {"ok": True}


# Основной webhook-эндпоинт (то, что указано в BotFather)
@app.post("/tg")
async def tg_webhook(data: dict):
    return await _process_update(data)


# Дополнительный алиас, если где-то остался старый путь
@app.post("/tg/webhook")
async def tg_webhook_legacy(data: dict):
    return await _process_update(data)
