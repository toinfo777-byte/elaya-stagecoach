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


# Заглушка вебхука (мы работаем в polling; эндпоинт может пригодиться позже)
@app.post("/tg/webhook")
async def tg_webhook(_: Request):
    return PlainTextResponse("ok")


# Core API (ядро сцен) — подключаем, если файл есть
try:
    from app.core_api import router as core_api_router  # type: ignore
    app.include_router(core_api_router)
    logging.getLogger(__name__).info("Core API router attached")
except Exception as e:
    logging.getLogger(__name__).warning("Core API not attached: %s", e)

# ── Aiogram (bot) ────────────────────────────────────────────────────────────
dp = Dispatcher()
PROFILE = os.getenv("BOT_PROFILE", "hq").strip().lower()

# Служебные/HQ-роутеры доступны в любом профиле
from app.routers import system, hq  # noqa: E402

dp.include_router(system.router)
dp.include_router(hq.router)

# Профильные подключения
if PROFILE == "trainer":
    # Тонкий портал: весь интеллект — в веб-ядре
    from app.routers import trainer  # noqa: E402
    dp.include_router(trainer.router)

elif PROFILE == "hq":
    # HQ-профиль: можешь подключить нужные штабные модули по мере надобности
    # Пример (раскомментируй необходимые):
    # from app.routers import entrypoints, onboarding, leader, training, progress, ...
    # dp.include_router(entrypoints.router)
    # dp.include_router(onboarding.router)
    # dp.include_router(leader.router)
    # dp.include_router(training.router)
    pass

# Храним бота и фоновой таск polling в состоянии приложения
app.state.bot: Bot | None = None
app.state.bot_task: asyncio.Task | None = None


async def _on_startup(bot: Bot):
    me = await bot.get_me()
    logging.info(
        ">>> Startup: %s as @%s | profile=%s | build=%s",
        me.id,
        me.username,
        PROFILE,
        BUILD_MARK,
    )


async def _on_shutdown(bot: Bot | None):
    if bot:
        await bot.session.close()
    logging.info(">>> Shutdown clean")


@app.on_event("startup")
async def on_startup():
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    )

    token = settings.TG_BOT_TOKEN or settings.BOT_TOKEN or os.getenv("TELEGRAM_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_TOKEN is not set")

    bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    app.state.bot = bot
    await _on_startup(bot)

    # Запускаем polling в фоне, чтобы FastAPI оставался отзывчивым
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
