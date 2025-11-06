# app/entrypoint_web.py
from __future__ import annotations

import os
import logging
from typing import Any

from fastapi import FastAPI, Request
from starlette.responses import PlainTextResponse
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.config import settings
from app.build import BUILD_MARK

app = FastAPI()

@app.get("/healthz")
async def healthz() -> PlainTextResponse:
    return PlainTextResponse("ok")

# Вебхук-эндпоинт (телега стучит сюда)
@app.post(settings.WEBHOOK_PATH or "/tg/webhook")  # безопасно если переменная есть
async def tg_webhook(_: Request) -> PlainTextResponse:
    # aiogram обрабатывает апдейты сам (через webhook runner)
    return PlainTextResponse("ok")

# ── Aiogram setup ─────────────────────────────────────────────────────────────
dp = Dispatcher()
BOT_PROFILE = os.getenv("BOT_PROFILE", "hq").strip().lower()

# Служебные HQ-роутеры без «фронтовых» клавиатур
from app.routers import system, hq
dp.include_router(system.router)
dp.include_router(hq.router)

if BOT_PROFILE == "trainer":
    # Подключаем только тренерские контроллеры (где клавиатуры и меню)
    from app.routers import training, progress, minicasting, leader, settings as settings_mod, faq
    dp.include_router(training.router)
    dp.include_router(progress.router)
    dp.include_router(minicasting.router)
    dp.include_router(leader.router)
    dp.include_router(settings_mod.router)
    dp.include_router(faq.router)
# если hq — ничего лишнего не добавляем

async def _startup_bot() -> Bot:
    token = settings.TG_BOT_TOKEN or settings.BOT_TOKEN or os.getenv("TELEGRAM_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_TOKEN/BOT_TOKEN is not set")
    bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    me = await bot.get_me()
    logging.info(">>> Startup: %s as @%s | profile=%s | build=%s",
                 me.id, me.username, BOT_PROFILE, BUILD_MARK)
    return bot

@app.on_event("startup")
async def on_startup() -> None:
    logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
    bot = await _startup_bot()
    # webhook режим: aiogram сам примет апдейты, мы только стартуем обработчик
    # allowed_updates авто-резолв
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

@app.on_event("shutdown")
async def on_shutdown() -> None:
    pass
