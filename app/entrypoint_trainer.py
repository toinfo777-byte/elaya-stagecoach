from __future__ import annotations

import os
import logging
from typing import Any

from fastapi import FastAPI, Request
from starlette.responses import Response, PlainTextResponse
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.config import settings
from app.build import BUILD_MARK

app = FastAPI(title="Elaya Trainer — webhook")
WEBHOOK_PATH: str = (
    os.getenv("WEBHOOK_PATH")
    or getattr(settings, "WEBHOOK_PATH", None)
    or "/tg/webhook"
)

dp = Dispatcher()
BOT_PROFILE = "trainer"  # фиксировано для этого сервиса

# Только тренерские роутеры
from app.routers import (  # noqa: E402
    system,  # системный /start (с меню для trainer)
    training, progress, minicasting, leader,
    settings as settings_mod, faq,
)
dp.include_router(system.router)
dp.include_router(training.router)
dp.include_router(progress.router)
dp.include_router(minicasting.router)
dp.include_router(leader.router)
dp.include_router(settings_mod.router)
dp.include_router(faq.router)


@app.get("/healthz")
async def healthz() -> PlainTextResponse:
    return PlainTextResponse("ok")


@app.post(WEBHOOK_PATH)
async def tg_webhook(request: Request) -> Response:
    update: Any = await request.json()
    bot: Bot = request.app.state.bot
    await dp.feed_webhook_update(bot, update)
    return Response(status_code=200)


async def _make_bot() -> Bot:
    token = (
        getattr(settings, "TG_BOT_TOKEN", None)
        or getattr(settings, "BOT_TOKEN", None)
        or os.getenv("TELEGRAM_TOKEN")
    )
    if not token:
        raise RuntimeError("TELEGRAM_TOKEN/BOT_TOKEN is not set")
    bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    me = await bot.get_me()
    logging.info(
        ">>> Startup (trainer): id=%s user=@%s build=%s",
        me.id, me.username, BUILD_MARK
    )
    return bot


@app.on_event("startup")
async def on_startup() -> None:
    log_level = getattr(settings, "LOG_LEVEL", "INFO")
    logging.basicConfig(level=getattr(logging, str(log_level).upper(), logging.INFO))
    app.state.bot = await _make_bot()


@app.on_event("shutdown")
async def on_shutdown() -> None:
    bot: Bot | None = getattr(app.state, "bot", None)
    if bot:
        await bot.session.close()
