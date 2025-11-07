from __future__ import annotations

import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from fastapi import FastAPI, Request
from starlette.responses import PlainTextResponse

from app.config import settings
from app.build import BUILD_MARK

# ── FastAPI (web) ─────────────────────────────────────────────────────────────
app = FastAPI()

@app.get("/healthz")
async def healthz():
    return PlainTextResponse("ok")

# (заглушка — мы работаем в polling; эндпоинт оставим на будущее)
@app.post("/tg/webhook")
async def tg_webhook(_: Request):
    return PlainTextResponse("ok")

# Подключаем Core API (ядро сцен)
try:
    from app.core_api import router as core_api_router
    app.include_router(core_api_router)
except Exception as e:
    # без core_api первый запуск тоже возможен; логируем мягко
    logging.getLogger(__name__).warning("core_api not attached: %s", e)

# ── Aiogram (bot) ────────────────────────────────────────────────────────────
dp = Dispatcher()
BOT_PROFILE = os.getenv("BOT_PROFILE", "hq").strip().lower()

# Служебные/HQ роутеры
from app.routers import system, hq
dp.include_router(system.router)
dp.include_router(hq.router)

if BOT_PROFILE == "trainer":
    # фронтовой контур (тонкий портал)
    from app.routers import trainer
    dp.include_router(trainer.router)
else:
    # профиль по умолчанию — «hq»: только штабные команды
    pass

# будем хранить задачу и бота в состоянии приложения
app.state.bot = None
app.state.bot_task = None

async def _on_startup(bot: Bot):
    me = await bot.get_me()
    logging.info(
        ">>> Startup: %s as @%s | profile=%s | build=%s",
        me.id, me.username, BOT_PROFILE, BUILD_MARK
    )

async def _on_shutdown(bot: Bot | None):
    if bot:
        await bot.session.close()
    logging.info(">>> Shutdown clean")

@app.on_event("startup")
async def on_startup():
    logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
    token = settings.TG_BOT_TOKEN or settings.BOT_TOKEN or os.getenv("TELEGRAM_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_TOKEN is not set")

    bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    app.state.bot = bot
    await _on_startup(bot)

    # Стартуем polling как фоновой таск, чтобы FastAPI не блокировался
    app.state.bot_task = asyncio.create_task(
        dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    )

@app.on_event("shutdown")
async def on_shutdown():
    # Останавливаем polling аккуратно
    task = app.state.bot_task
    if task and not task.done():
        task.cancel()
        try:
            await task
        except Exception:
            pass
    await _on_shutdown(app.state.bot)
