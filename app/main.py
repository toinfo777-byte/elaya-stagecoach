# app/main.py
from __future__ import annotations

import asyncio
import logging
import os
import time
from importlib import import_module
from typing import Optional

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Update

from fastapi import FastAPI, Request, Response

# ──────────────────────────────────────────────
START_TS = time.time()

def env(name: str, default: str = "") -> str:
    v = os.getenv(name)
    return (v if v is not None else default).strip()

MODE = env("MODE", "worker")  # worker | web | webhook
ENV  = env("ENV", "develop")
BOT_TOKEN = env("BOT_TOKEN") or env("TELEGRAM_TOKEN")
WEBHOOK_BASE = env("WEBHOOK_BASE")  # https://<host>
WEBHOOK_PATH = env("WEBHOOK_PATH")  # /tg/<secret>
WEBHOOK_SECRET = env("WEBHOOK_SECRET")

BUILD_MARK = env("BUILD_MARK", "local")
SHORT_SHA  = env("SHORT_SHA", "local")

logging.basicConfig(
    level=getattr(logging, env("LOG_LEVEL", "INFO")),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
log = logging.getLogger("main")

# ──────────────────────────────────────────────
async def _include_routers(dp: Dispatcher) -> None:
    """Импортирует базовые роутеры проекта."""
    for module_name in ("app.routers.control", "app.routers.hq"):
        try:
            mod = import_module(module_name)
            dp.include_router(getattr(mod, "router"))
            log.info("✅ router loaded: %s", module_name)
        except Exception:
            log.exception("❌ router failed: %s", module_name)
            raise

def _uptime_sec() -> int:
    return int(time.time() - START_TS)

# ──────────────────────────────────────────────
# POLLING MODE (для prod)
async def run_polling() -> None:
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is required for polling mode")

    bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    await _include_routers(dp)

    await bot.delete_webhook(drop_pending_updates=True)
    log.info("🚀 Start polling… [%s | %s]", BUILD_MARK, SHORT_SHA[:7])
    await dp.start_polling(bot)

# ──────────────────────────────────────────────
# WEB STATUS MODE (для health-check и статусов)
def build_web_app_status() -> FastAPI:
    app = FastAPI(title="Elaya StageCoach (status)", version=BUILD_MARK)

    @app.get("/status_json")
    async def status_json():
        return {
            "build": BUILD_MARK,
            "sha": SHORT_SHA,
            "uptime_sec": _uptime_sec(),
            "env": ENV,
            "mode": "web",
            "bot_id": None,
        }

    return app

# ──────────────────────────────────────────────
# WEBHOOK MODE (для staging)
def build_web_app_webhook() -> FastAPI:
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is required for webhook mode")
    if not (WEBHOOK_BASE and WEBHOOK_PATH and WEBHOOK_SECRET):
        raise RuntimeError("WEBHOOK_BASE/WEBHOOK_PATH/WEBHOOK_SECRET required")

    bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    app = FastAPI(title="Elaya StageCoach (webhook)", version=BUILD_MARK)

    @app.on_event("startup")
    async def on_startup():
        await _include_routers(dp)
        url = f"{WEBHOOK_BASE}{WEBHOOK_PATH}"
        await bot.delete_webhook(drop_pending_updates=True)
        await bot.set_webhook(
            url=url,
            secret_token=WEBHOOK_SECRET,
            drop_pending_updates=True,
        )
        log.info("✅ setWebhook: %s", url)

    @app.on_event("shutdown")
    async def on_shutdown():
        await bot.session.close()

    @app.get("/status_json")
    async def status_json():
        me = None
        try:
            me = await bot.get_me()
        except Exception:
            pass
        return {
            "build": BUILD_MARK,
            "sha": SHORT_SHA,
            "uptime_sec": _uptime_sec(),
            "env": ENV,
            "mode": "webhook",
            "bot_id": getattr(me, "id", None),
            "bot_username": getattr(me, "username", None),
        }

    @app.post(WEBHOOK_PATH)
    async def tg_webhook(request: Request) -> Response:
        if request.headers.get("X-Telegram-Bot-Api-Secret-Token") != WEBHOOK_SECRET:
            return Response(status_code=403)

        data = await request.json()
        try:
            update = Update.model_validate(data)
        except Exception:
            return Response(status_code=400)

        await dp.feed_update(bot, update)
        return Response(status_code=200)

    return app

# ──────────────────────────────────────────────
# ENTRYPOINT
if __name__ == "__main__":
    import uvicorn
    if MODE == "worker":
        asyncio.run(run_polling())
    elif MODE == "web":
        uvicorn.run(build_web_app_status, host="0.0.0.0", port=8000, factory=True)
    elif MODE == "webhook":
        uvicorn.run(build_web_app_webhook, host="0.0.0.0", port=8000, factory=True)
    else:
        raise RuntimeError(f"Unknown MODE: {MODE}")
