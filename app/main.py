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

# ---------------------------- env helpers -----------------------------------
def env(name: str, default: str = "") -> str:
    v = os.getenv(name)
    return (v if v is not None else default).strip()

START_TS = time.time()

MODE = env("MODE", "worker")          # worker | web | webhook
ENV  = env("ENV", "develop")

BOT_TOKEN       = env("BOT_TOKEN") or env("TELEGRAM_TOKEN")
WEBHOOK_BASE    = env("WEBHOOK_BASE")        # e.g. https://elaya-stagecoach-web.onrender.com
WEBHOOK_PATH    = env("WEBHOOK_PATH")        # e.g. /tg/<secret>
WEBHOOK_SECRET  = env("WEBHOOK_SECRET")      # same <secret> value

BUILD_MARK = env("BUILD_MARK", "local")
SHORT_SHA  = env("SHORT_SHA", env("BUILD_SHA", "local"))

LOG_LEVEL = env("LOG_LEVEL", "INFO")

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

# --------------------------- routers include --------------------------------
async def _include_routers(dp: Dispatcher) -> None:
    """
    Подключаем только стабильные роутеры.
    Важно: проблемный app.routers.control исключён, чтобы не падал импорт.
    """
    modules = (
        "app.routers.faq",
        "app.routers.devops_sync",
        "app.routers.panic",
        "app.routers.hq",
    )
    for module_name in modules:
        try:
            mod = import_module(module_name)
            dp.include_router(getattr(mod, "router"))
            logging.info("✅ router loaded: %s", module_name)
        except Exception as e:
            logging.error("❌ router failed: %s — %r", module_name, e)

def _uptime_sec() -> int:
    return int(time.time() - START_TS)

# ----------------------------- polling mode ---------------------------------
async def run_polling() -> None:
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is required for polling mode")

    bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    # на всякий случай снимаем webhook, чтобы Telegram не конфликтовал с getUpdates
    try:
        await bot.delete_webhook(drop_pending_updates=True)
    except Exception as e:
        logging.warning("delete_webhook failed: %r", e)

    await _include_routers(dp)
    me = await bot.get_me()
    logging.info("🚀 Start polling… [%s | %s] @%s", BUILD_MARK, SHORT_SHA[:7], me.username)
    await dp.start_polling(bot)

# --------------------------- web status only --------------------------------
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

# ---------------------------- webhook mode ----------------------------------
def build_web_app_webhook() -> FastAPI:
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is required for webhook mode")
    if not (WEBHOOK_BASE and WEBHOOK_PATH and WEBHOOK_SECRET):
        raise RuntimeError("WEBHOOK_BASE/WEBHOOK_PATH/WEBHOOK_SECRET are required for webhook mode")

    bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    app = FastAPI(title="Elaya StageCoach (webhook)", version=BUILD_MARK)

    @app.on_event("startup")
    async def on_startup():
        await _include_routers(dp)
        url = f"{WEBHOOK_BASE}{WEBHOOK_PATH}"
        # снимаем старый, ставим новый — с drop_pending_updates
        await bot.delete_webhook(drop_pending_updates=True)
        await bot.set_webhook(
            url=url,
            secret_token=WEBHOOK_SECRET,
            drop_pending_updates=True,
        )
        logging.info("✅ setWebhook: %s", url)

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
        # проверка секрета Telegram
        if request.headers.get("X-Telegram-Bot-Api-Secret-Token") != WEBHOOK_SECRET:
            return Response(status_code=403)

        try:
            data = await request.json()
            update = Update.model_validate(data)  # pydantic v2
        except Exception:
            return Response(status_code=400)

        await dp.feed_update(bot, update)
        return Response(status_code=200)

    return app

# -------------------------------- entrypoint --------------------------------
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
