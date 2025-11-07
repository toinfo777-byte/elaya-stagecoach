# app/main.py
from __future__ import annotations

import asyncio
import logging
import os
import time
from typing import Any

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Request
from fastapi import FastAPI, Request
from starlette.responses import PlainTextResponse

from app.build import BUILD_MARK
from app.config import settings

# Роутеры
from app.routers import system, hq  # базовые штабные
from app.routers import trainer  # фронтовой контур
from app.routers import diag  # диагностика

# Core API (новый)
from app.core_api import router as core_api_router

# Middleware Sentry
from app.mw_sentry import SentryBreadcrumbs

# ---------------------------------------------------------------------------

app = FastAPI()
app.add_middleware(SentryBreadcrumbs)

dp = Dispatcher()

BOT_PROFILE = os.getenv("BOT_PROFILE", "hq").strip().lower()
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "").strip()

# Подключаем базовые и безопасные роутеры
app.include_router(system.router)
app.include_router(hq.router)
app.include_router(diag.router)
app.include_router(core_api_router)

if BOT_PROFILE == "trainer":
    dp.include_router(trainer.router)

# ---------------------------------------------------------------------------

@app.get("/healthz")
async def healthz() -> PlainTextResponse:
    return PlainTextResponse("ok")

# ---------------------------------------------------------------------------
# Webhook endpoint (универсальный, для Telegram)
# ---------------------------------------------------------------------------

from aiogram.types import Update
import sentry_sdk


@app.post("/tg/webhook")
async def tg_webhook(request: Request):
    """
    Принимает Telegram Update и передаёт его в Aiogram Dispatcher.
    """
    if request.headers.get("x-telegram-bot-api-secret-token") != WEBHOOK_SECRET:
        return PlainTextResponse("forbidden", status_code=403)

    data = await request.json()
    try:
        update = Update.model_validate(data)
    except Exception:
        return PlainTextResponse("bad update", status_code=400)

    # Добавляем breadcrumbs в Sentry
    uid = getattr(getattr(update, "message", None), "from_user", None)
    uid = getattr(uid, "id", None)
    sentry_sdk.add_breadcrumb(
        category="tg.update",
        message="incoming update",
        level="info",
        data={
            "chat_id": getattr(getattr(update, "message", None), "chat", None)
            and update.message.chat.id,
            "user_id": uid,
            "has_text": bool(
                getattr(getattr(update, "message", None), "text", None)
            ),
        },
    )

    bot = Bot(
        token=settings.TELEGRAM_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    await dp.feed_update(bot, update)
    return PlainTextResponse("ok", status_code=200)

# ---------------------------------------------------------------------------
# События запуска и завершения
# ---------------------------------------------------------------------------

@app.on_event("startup")
async def on_startup():
    logging.info(">>> Startup: build=%s profile=%s", BUILD_MARK, BOT_PROFILE)


@app.on_event("shutdown")
async def on_shutdown():
    logging.info(">>> Shutdown complete.")


# ---------------------------------------------------------------------------
# Для Render (Uvicorn)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 10000)),
        log_level="info",
    )
