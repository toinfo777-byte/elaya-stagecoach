# app/bot/main.py
from __future__ import annotations

import os

from fastapi import FastAPI, Request, HTTPException
from aiogram import Bot, Dispatcher
from aiogram.types import Update

from app.config import settings  # можно использовать токен и прочее из настроек

# токен: сначала из Settings, потом из окружения
BOT_TOKEN = (
    getattr(settings, "tg_bot_token", None)
    or getattr(settings, "bot_token", None)
    or os.getenv("TG_BOT_TOKEN", "")
).strip()

if not BOT_TOKEN:
    raise RuntimeError("TG_BOT_TOKEN / TELEGRAM_TOKEN / BOT_TOKEN is not set")

WEBHOOK_SECRET = (
    getattr(settings, "webhook_secret", None)
    or os.getenv("TG_WEBHOOK_SECRET", "")
).strip()

bot = Bot(BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher()

# подключаем все роутеры тренера
from app.routers import start as start_router
from app.routers import menu, help, policy, progress, reviews

for r in (
    start_router.router,
    menu.router,
    help.router,
    policy.router,
    progress.router,
    reviews.router,
):
    dp.include_router(r)

app = FastAPI()


@app.get("/healthz")
async def healthz():
    return {"ok": True}


@app.post("/tg/webhook")
async def tg_webhook(request: Request):
    # простая защита по секрету (если настроен)
    if WEBHOOK_SECRET:
        header = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
        if header != WEBHOOK_SECRET:
            raise HTTPException(status_code=401, detail="invalid secret token")

    data = await request.json()
    update = Update.model_validate(data)
    await dp.feed_update(bot, update)
    return {"ok": True}
