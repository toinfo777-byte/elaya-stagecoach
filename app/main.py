from __future__ import annotations

import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from fastapi import FastAPI
from starlette.responses import PlainTextResponse

from app.config import settings
from app.build import BUILD_MARK

# ── FastAPI (web) ─────────────────────────────────────────────────────────────
app = FastAPI()

@app.get("/healthz")
async def healthz():
    return PlainTextResponse("ok")

# Точка входа вебхука для обоих профилей
@app.post("/tg/webhook")
async def tg_webhook(request):
    # aiogram v3 интеграция через polling webhook handler подключается в startup
    return PlainTextResponse("ok")

# ── Aiogram (bot) ────────────────────────────────────────────────────────────
dp = Dispatcher()
BOT_PROFILE = os.getenv("BOT_PROFILE", "hq").strip().lower()

# Подключаем общесистемные HQ-команды (без меню/клавиатуры)
from app.routers import system, hq  # HQ всегда доступен для служебных
dp.include_router(system.router)
dp.include_router(hq.router)

if BOT_PROFILE == "trainer":
    # фронтовой контур
    from app.routers import trainer
    dp.include_router(trainer.router)
else:
    # профиль по умолчанию — «hq»: только штабные команды
    pass

async def _on_startup(bot: Bot):
    me = await bot.get_me()
    logging.info(">>> Startup: %s as @%s | profile=%s | build=%s",
                 me.id, me.username, BOT_PROFILE, BUILD_MARK)

async def _on_shutdown(bot: Bot):
    await bot.session.close()
    logging.info(">>> Shutdown clean")

@app.on_event("startup")
async def on_startup():
    logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
    token = settings.TG_BOT_TOKEN or settings.BOT_TOKEN or os.getenv("TELEGRAM_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_TOKEN is not set")

    bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await _on_startup(bot)

    # webhook-режим — адрес указывается на стороне Telegram
    # мы просто поднимаем обработчики
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

@app.on_event("shutdown")
async def on_shutdown():
    # aiogram сам останавливает диспетчер; чистим сессии в _on_shutdown
    pass
