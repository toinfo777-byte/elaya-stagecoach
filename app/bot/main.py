from __future__ import annotations

import os

from fastapi import FastAPI, Request, HTTPException
from aiogram import Bot, Dispatcher
from aiogram.types import Update

from app.routers import router as root_router  # главный router с /start (и дальше всем остальным)

BOT_TOKEN = os.getenv("TG_BOT_TOKEN", "").strip()
if not BOT_TOKEN:
    raise RuntimeError("TG_BOT_TOKEN is not set")

WEBHOOK_SECRET = os.getenv("TG_WEBHOOK_SECRET", "").strip()

bot = Bot(BOT_TOKEN)
dp = Dispatcher()
dp.include_router(root_router)   # <-- один вход

app = FastAPI()


@app.get("/healthz")
async def healthz():
    return {"ok": True}


@app.post("/tg/webhook")
async def tg_webhook(request: Request):
    # простая защита по секрету (опционально)
    if WEBHOOK_SECRET:
        header = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
        if header != WEBHOOK_SECRET:
            raise HTTPException(status_code=401, detail="invalid secret token")

    data = await request.json()
    update = Update.model_validate(data)
    await dp.feed_update(bot, update)

    return {"ok": True}
