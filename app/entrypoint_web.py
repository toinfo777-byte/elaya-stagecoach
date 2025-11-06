from __future__ import annotations

import logging
import os
from typing import Optional

from fastapi import FastAPI, Request
from starlette.responses import PlainTextResponse, Response
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.config import settings
from app.build import BUILD_MARK

app = FastAPI(title="Elaya Stagecoach — webhook")

# ── Aiogram setup ─────────────────────────────────────────────────────────────
dp = Dispatcher()
_bot: Optional[Bot] = None

# Служебные HQ-роутеры (без фронтовых клавиатур)
from app.routers import system, hq  # noqa: E402

dp.include_router(system.router)
dp.include_router(hq.router)

if settings.bot_profile == "trainer":
    # Подключаем только «фронтовые» разделы для тренера
    from app.routers import (  # noqa: E402
        training, progress, minicasting, leader, settings as settings_mod, faq,
    )
    dp.include_router(training.router)
    dp.include_router(progress.router)
    dp.include_router(minicasting.router)
    dp.include_router(leader.router)
    dp.include_router(settings_mod.router)
    dp.include_router(faq.router)
# если profile == "hq" — ничего лишнего не добавляем

# ── Probes ────────────────────────────────────────────────────────────────────
@app.get("/healthz")
async def healthz() -> PlainTextResponse:
    return PlainTextResponse("ok")


# Вебхук-эндпоинт: сюда стучится Telegram
@app.post("/tg/webhook")
async def tg_webhook(request: Request) -> Response:
    # Никаких авто-«Webhook alert»
    global _bot
    if _bot is None:
        return Response(status_code=503)
    update = await request.json()
    await dp.feed_webhook_update(_bot, update)
    return Response(status_code=200)


# ── Lifecycle ────────────────────────────────────────────────────────────────
async def _make_bot() -> Bot:
    token = (
        settings.tg_bot_token
        or settings.bot_token
        or os.getenv("TELEGRAM_TOKEN")
    )
    if not token:
        raise RuntimeError("TELEGRAM_TOKEN/BOT_TOKEN is not set")
    bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    me = await bot.get_me()
    logging.info(
        ">>> Startup: %s as @%s | profile=%s | build=%s",
        me.id, me.username, settings.bot_profile, BUILD_MARK,
    )
    return bot


@app.on_event("startup")
async def on_startup() -> None:
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO)
    )
    global _bot
    _bot = await _make_bot()
    # В вебхуковом режиме dp.start_polling НЕ вызываем


@app.on_event("shutdown")
async def on_shutdown() -> None:
    global _bot
    if _bot is not None:
        await _bot.session.close()
        _bot = None
