from __future__ import annotations

import os
import logging
from typing import Any

from fastapi import FastAPI, Request
from starlette.responses import PlainTextResponse, Response
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.config import settings
from app.build import BUILD_MARK

# ── FastAPI ───────────────────────────────────────────────────────────────────
app = FastAPI(title="Elaya Stagecoach — webhook")
WEBHOOK_PATH: str = (
    os.getenv("WEBHOOK_PATH")
    or getattr(settings, "WEBHOOK_PATH", None)
    or "/tg/webhook"
)

# ── Aiogram ───────────────────────────────────────────────────────────────────
dp = Dispatcher()
BOT_PROFILE = os.getenv("BOT_PROFILE", "hq").strip().lower()

# Служебные роутеры (без фронтовых меню)
from app.routers import system, hq  # noqa: E402
dp.include_router(system.router)
dp.include_router(hq.router)

# Подключаем тренерские роутеры ТОЛЬКО если профиль trainer
if BOT_PROFILE == "trainer":
    from app.routers import (  # noqa: E402
        training,
        progress,
        minicasting,
        leader,
        settings as settings_mod,
        faq,
    )
    dp.include_router(training.router)
    dp.include_router(progress.router)
    dp.include_router(minicasting.router)
    dp.include_router(leader.router)
    dp.include_router(settings_mod.router)
    dp.include_router(faq.router)

# ── Healthz ───────────────────────────────────────────────────────────────────
@app.get("/healthz")
async def healthz() -> PlainTextResponse:
    return PlainTextResponse("ok")


# ── Webhook endpoint ──────────────────────────────────────────────────────────
@app.post(WEBHOOK_PATH)
async def tg_webhook(request: Request) -> Response:
    """
    Принимаем JSON-апдейт и передаём его в aiogram.
    Никаких автосообщений/«Webhook alert» здесь нет.
    """
    update: Any = await request.json()
    bot: Bot = request.app.state.bot  # задан в startup
    await dp.feed_webhook_update(bot, update)
    return Response(status_code=200)


# ── Startup / Shutdown ────────────────────────────────────────────────────────
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
        ">>> Startup: id=%s user=@%s profile=%s build=%s",
        me.id, me.username, BOT_PROFILE, BUILD_MARK
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
