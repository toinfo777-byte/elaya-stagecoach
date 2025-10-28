from __future__ import annotations

import asyncio
import importlib
import logging
import os
from typing import Iterable

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Update
from fastapi import FastAPI, Request, HTTPException

from app.config import settings

# ---------- Логирование ----------
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
log = logging.getLogger("main")

# ---------- Бот/Диспетчер ----------
bot = Bot(
    token=settings.BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode(settings.PARSE_MODE)),
)
dp = Dispatcher()


# ---------- Подключение роутеров (стабильные) ----------
async def _include_routers(dp_: Dispatcher) -> None:
    """
    Подключаем только стабильные модули.
    ВАЖНО: проблемный app.routers.control НЕ подключаем (заглушка лежит отдельно).
    """
    modules: Iterable[str] = (
        "app.routers.entrypoints",
        # "app.routers.control",  # ← вернёшь позже при необходимости
        # ниже можно по одному добавлять стабильные модули
        # "app.routers.faq",
        # "app.routers.devops_sync",
        # "app.routers.panic",
        # "app.routers.hq",
    )
    for module_name in modules:
        try:
            mod = importlib.import_module(module_name)
            router = getattr(mod, "router", None)
            if router is None:
                log.warning("module %s has no `router`, skipped", module_name)
                continue
            dp_.include_router(router)
            log.info("router loaded: %s", module_name)
        except Exception:
            log.exception("❌ router failed: %s", module_name)
            raise


# ---------- Режимы работы ----------
app = FastAPI(title="Elaya StageCoach — Web")

WEBHOOK_PATH = f"/tg/{settings.WEBHOOK_SECRET}"
WEBHOOK_URL = f"{settings.WEB_BASE_URL.rstrip('/')}{WEBHOOK_PATH}"


@app.on_event("startup")
async def on_startup() -> None:
    await _include_routers(dp)
    if settings.MODE == "web":
        # Ставим webhook
        await bot.set_webhook(
            url=WEBHOOK_URL,
            allowed_updates=list(settings.WEBHOOK_ALLOWED_UPDATES),
            drop_pending_updates=True,
        )
        log.info("✅ setWebhook: %s", WEBHOOK_URL)
    else:
        # polling запускаем в фоне, чтобы FastAPI тоже мог подняться при режиме локального теста
        asyncio.create_task(run_polling())


@app.on_event("shutdown")
async def on_shutdown() -> None:
    if settings.MODE == "web":
        try:
            await bot.delete_webhook(drop_pending_updates=True)
        except Exception:
            log.exception("delete_webhook failed")


@app.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    if settings.MODE != "web":
        raise HTTPException(status_code=400, detail="Not in webhook mode")
    data = await request.json()
    update = Update.model_validate(data)
    await dp.feed_update(bot, update)
    return {"ok": True}


async def run_polling() -> None:
    log.info("🚀 Start polling…")
    await _include_routers(dp)
    # На всякий случай удалим webhook перед polling.
    try:
        await bot.delete_webhook(drop_pending_updates=True)
    except Exception:
        pass
    await dp.start_polling(bot)


# Для Render Web-сервиса — простой health-check
@app.get("/")
async def root():
    return {"service": "elaya-stagecoach-web", "mode": settings.MODE, "build": settings.BUILD_MARK, "sha": settings.SHORT_SHA}
