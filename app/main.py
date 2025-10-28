from __future__ import annotations

import asyncio
import importlib
import logging
import os
from typing import Any

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Update
from fastapi import FastAPI, Request

from app.config import settings

# -------------------------------------------------
# Логирование
# -------------------------------------------------
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
log = logging.getLogger("main")

# -------------------------------------------------
# Инициализация бота/диспетчера
# -------------------------------------------------
# DefaultBotProperties принимает строку, поэтому settings.PARSE_MODE ок
bot = Bot(
    token=settings.BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=settings.PARSE_MODE),
)
dp = Dispatcher()

# -------------------------------------------------
# Подключение стабильных роутеров
# -------------------------------------------------
async def _include_routers(dp: Dispatcher) -> None:
    """
    Подключаем только стабильные роутеры.
    ВНИМАНИЕ: app.routers.control исключён.
    """
    modules = (
        "app.routers.faq",
        "app.routers.devops_sync",
        "app.routers.panic",
        "app.routers.hq",
    )
    for module_name in modules:
        try:
            mod = importlib.import_module(module_name)
            if hasattr(mod, "router"):
                dp.include_router(mod.router)  # type: ignore[attr-defined]
                log.info("router loaded: %s", module_name)
            else:
                log.warning("module %s has no 'router'", module_name)
        except Exception as e:
            log.error("router failed: %s", module_name, exc_info=e)
            raise

# -------------------------------------------------
# Режимы запуска: WEB (webhook) / WORKER (polling)
# -------------------------------------------------
app = FastAPI(title="Elaya Stagecoach Web") if settings.MODE == "web" else None

async def _startup_common() -> None:
    await _include_routers(dp)

# ---------- WEBHOOK ----------
if settings.MODE == "web":
    assert app is not None

    @app.on_event("startup")
    async def on_startup() -> None:
        await _startup_common()
        # ставим вебхук
        url = settings.webhook_url  # валидирует WEB_BASE_URL
        await bot.set_webhook(url, drop_pending_updates=True)
        log.info("setWebhook: %s", url)
        log.info("Application startup complete. Uvicorn will serve FastAPI.")

    @app.on_event("shutdown")
    async def on_shutdown() -> None:
        await bot.session.close()

    @app.get("/")
    async def root() -> dict[str, Any]:
        return {
            "ok": True,
            "env": settings.ENV,
            "mode": settings.MODE,
            "build": settings.BUILD_MARK,
            "sha": settings.SHORT_SHA,
        }

    @app.post("/tg/{token}")
    async def telegram_webhook(token: str, request: Request) -> dict[str, Any]:
        if token != settings.BOT_TOKEN:
            return {"ok": False}
        data = await request.json()
        update = Update.model_validate(data)
        await dp.feed_update(bot, update)
        return {"ok": True}

# ---------- POLLING WORKER ----------
async def run_polling() -> None:
    await _startup_common()
    log.info("🚀 Start polling…")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == "__main__":
    # Локальный запуск: MODE=worker → polling
    if settings.MODE in {"worker", "polling"}:
        asyncio.run(run_polling())
