# app/main.py
from __future__ import annotations

import os
import logging
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import FastAPI, Request
from starlette.responses import PlainTextResponse, Response
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.config import settings
from app.build import BUILD_MARK

# FastAPI-роутер ядра (event/timeline)
from app.routers import system as api_system
# Aiogram-роутер HQ
from app.routers import hq

# ── Константы ядра ────────────────────────────────────────────────────────────

BOT_PROFILE = os.getenv("BOT_PROFILE", "hq").strip().lower()
CORE_VERSION = os.getenv("ELAYA_CORE_VERSION", "core-0.5.x")

# ── FastAPI ───────────────────────────────────────────────────────────────────

app = FastAPI(title="Elaya Stagecoach — webhook")

WEBHOOK_PATH: str = (
    os.getenv("WEBHOOK_PATH")
    or getattr(settings, "WEBHOOK_PATH", None)
    or "/tg/webhook"
)

# подключаем REST-ядро: /api/event, /api/timeline
app.include_router(api_system.router)

# ── Aiogram ───────────────────────────────────────────────────────────────────

dp = Dispatcher()


# HQ-команды
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


# ── Healthz + Status (WEB-ядро) ───────────────────────────────────────────────

# Старый healthz оставляем для совместимости
@app.get("/healthz")
async def healthz_root() -> PlainTextResponse:
    """
    Простой текстовый healthcheck, который уже был.
    """
    return PlainTextResponse("ok")


@app.get("/api/healthz")
async def healthz_api() -> dict[str, str]:
    """
    Healthcheck для Docker/Render: бьём сюда из HEALTHCHECK.
    """
    return {"status": "ok"}


@app.get("/api/status")
async def status_api() -> dict[str, str]:
    """
    Мини-статус ядра: время, версия, билд и профиль.
    """
    now = datetime.now(timezone.utc).isoformat()
    return {
        "status": "ok",
        "time": now,
        "version": CORE_VERSION,
        "build": BUILD_MARK,
        "profile": BOT_PROFILE,
    }


# ── Webhook endpoint ──────────────────────────────────────────────────────────

@app.post(WEBHOOK_PATH)
async def tg_webhook(request: Request) -> Response:
    """
    Принимаем JSON-апдейт и передаём его в aiogram.
    Если бота нет (локальный запуск без токена) — отвечаем 503.
    """
    bot: Optional[Bot] = getattr(request.app.state, "bot", None)
    if bot is None:
        # вебхук не сконфигурирован, но ядро живёт
        return Response(status_code=503)

    update: Any = await request.json()
    await dp.feed_webhook_update(bot, update)
    return Response(status_code=200)


# ── Startup / Shutdown ────────────────────────────────────────────────────────

async def _make_bot() -> Optional[Bot]:
    """
    Пытаемся создать бота.
    Если токена нет — возвращаем None и не ломаем старт приложения.
    """
    token = (
        getattr(settings, "TG_BOT_TOKEN", None)
        or getattr(settings, "BOT_TOKEN", None)
        or os.getenv("TELEGRAM_TOKEN")
    )
    if not token:
        logging.warning("TELEGRAM_TOKEN/BOT_TOKEN is not set; bot will not be started.")
        return None

    bot = Bot(
        token=token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    me = await bot.get_me()
    logging.info(
        ">>> Startup: id=%s user=@%s profile=%s build=%s",
        me.id,
        me.username,
        BOT_PROFILE,
        BUILD_MARK,
    )
    return bot


@app.on_event("startup")
async def on_startup() -> None:
    log_level = getattr(settings, "LOG_LEVEL", "INFO")
    logging.basicConfig(
        level=getattr(logging, str(log_level).upper(), logging.INFO)
    )
    app.state.bot = await _make_bot()


@app.on_event("shutdown")
async def on_shutdown() -> None:
    bot: Optional[Bot] = getattr(app.state, "bot", None)
    if bot:
        await bot.session.close()
