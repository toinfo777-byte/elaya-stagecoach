from __future__ import annotations

import hmac
import os
from hashlib import sha256
from typing import Any

from aiogram import Bot, Dispatcher
from aiogram.types import Update
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import PlainTextResponse

from app.routers import hq_status  # <-- наш роутер

BOT_TOKEN = os.environ["BOT_TOKEN"]  # обязательно в переменных окружения
BASE_URL = os.getenv("WEB_BASE_URL")  # напр.: https://elaya-stagecoach-web.onrender.com
WEBHOOK_PATH = "/tg/webhook"
SECRET_TOKEN = os.getenv("WEBHOOK_SECRET", "")  # опционально

bot = Bot(BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher()
dp.include_router(hq_status.router)

app = FastAPI(title="Elaya Webhook")

@app.get("/healthz", response_class=PlainTextResponse)
async def healthz() -> str:
    return "OK"

@app.on_event("startup")
async def on_startup() -> None:
    # Ставим вебхук только если BASE_URL задан (в Render — должен быть)
    if not BASE_URL:
        return
    target = f"{BASE_URL}{WEBHOOK_PATH}"
    await bot.set_webhook(
        url=target,
        allowed_updates=["message"],  # нам этого достаточно для /status, /ping
        secret_token=SECRET_TOKEN or None,
        drop_pending_updates=True,
    )

@app.on_event("shutdown")
async def on_shutdown() -> None:
    # Отвяжем вебхук корректно (не обязательно)
    try:
        await bot.delete_webhook(drop_pending_updates=False)
    except Exception:
        pass

@app.post(WEBHOOK_PATH)
async def tg_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: str | None = Header(default=None),
) -> Any:
    # Если секрет задан — проверяем
    if SECRET_TOKEN:
        if not x_telegram_bot_api_secret_token:
            raise HTTPException(status_code=401, detail="Missing secret")
        if not hmac.compare_digest(x_telegram_bot_api_secret_token, SECRET_TOKEN):
            raise HTTPException(status_code=403, detail="Bad secret")

    data = await request.json()
    update = Update.model_validate(data)
    await dp.feed_update(bot, update)
    return {"ok": True}
