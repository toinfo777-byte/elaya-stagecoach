from __future__ import annotations

import os

from fastapi import FastAPI, Request, HTTPException
from aiogram import Bot, Dispatcher
from aiogram.types import Update

from app.config import settings
from app.routers import menu, reviews  # сюда позже добавим help, policy, progress

# --- токен и секрет вебхука ---

BOT_TOKEN = (
    os.getenv("TG_BOT_TOKEN", "").strip()
    or os.getenv("BOT_TOKEN", "").strip()
    or (settings.tg_bot_token or "")  # на случай, если используем Settings
    or (settings.bot_token or "")
)

if not BOT_TOKEN:
    raise RuntimeError("TG_BOT_TOKEN/BOT_TOKEN is not set")

WEBHOOK_SECRET = os.getenv("TG_WEBHOOK_SECRET", "").strip() or (
    (settings.webhook_secret or "") if hasattr(settings, "webhook_secret") else ""
)

# --- aiogram ---

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

# порядок не критичен; главное — чтобы reviews.router точно был подключён
for r in (
    menu.router,
    reviews.router,
):
    dp.include_router(r)

# --- FastAPI ---

app = FastAPI(title="Elaya Trainer — webhook")


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
