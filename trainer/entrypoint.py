# trainer/entrypoint.py
from __future__ import annotations

import logging
import os

from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Update

from app.routes import router as routes_router


def _get_bot_token() -> str:
    for name in ("TRAINER_BOT_TOKEN", "BOT_TOKEN", "TELEGRAM_BOT_TOKEN"):
        token = os.getenv(name, "").strip()
        if token:
            return token
    raise RuntimeError("Trainer bot token is not set")


logging.basicConfig(level=logging.INFO)

bot = Bot(
    token=_get_bot_token(),
    default=DefaultBotProperties(parse_mode="HTML"),
)
dp = Dispatcher()
dp.include_router(routes_router)

app = FastAPI()


@app.get("/healthz")
async def healthz():
    return {"ok": True, "status": "healthy"}


@app.post("/tg/webhook")
async def telegram_webhook(request: Request):
    payload = await request.json()
    update = Update.model_validate(payload)
    await dp.feed_update(bot, update)
    return {"ok": True}
