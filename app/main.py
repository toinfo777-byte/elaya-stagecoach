# app/main.py
from __future__ import annotations

import asyncio
import logging
import os
import time
from importlib import import_module
from typing import Iterable

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Update

from fastapi import FastAPI, Request, Response

START_TS = time.time()


def env(name: str, default: str = "") -> str:
    v = os.getenv(name)
    return (v if v is not None else default).strip()


# ── ENV ──────────────────────────────────────────────────────────────────────
MODE = env("MODE", "worker")  # worker | web | webhook
ENV = env("ENV", "develop")

BOT_TOKEN = env("BOT_TOKEN") or env("TELEGRAM_TOKEN") or env("TELEGRAM_TOKEN_PROD")

WEBHOOK_BASE = env("WEBHOOK_BASE")            # e.g. https://elaya-stagecoach-web.onrender.com
WEBHOOK_SECRET = env("WEBHOOK_SECRET")        # long random string
WEBHOOK_PATH = env("WEBHOOK_PATH")            # e.g. /tg/<secret>

BUILD_MARK = env("BUILD_MARK", "local")
SHORT_SHA = env("SHORT_SHA", "local")

LOG_LEVEL = env("LOG_LEVEL", "INFO")

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)


def _uptime_sec() -> int:
    return int(time.time() - START_TS)


# Подключаем существующие роутеры: список составлен по твоему прежнему main.py.
# Любой отсутствующий модуль будет пропущен без падения.
ROUTERS: Iterable[str] = (
    "app.routers.entrypoints",
    "app.routers.help",
    "app.routers.cmd_aliases",
    "app.routers.onboarding",
    "app.routers.system",
    "app.routers.minicasting",
    "app.routers.leader",
    "app.routers.training",
    "app.routers.progress",
    "app.routers.privacy",
    "app.routers.settings",
    "app.routers.extended",
    "app.routers.casting",
    "app.routers.apply",
    "app.routers.faq",
    "app.routers.devops_sync",
    "app.routers.panic",
    "app.routers.hq",
)


async def _include_routers(dp: Dispatcher) -> None:
    for module_name in ROUTERS:
        try:
            mod = import_module(module_name)
            router = getattr(mod, "router", None)
            if router is None:
                logging.warning("⚠️ %s: router not found — skipped", module_name)
                continue
            dp.include_router(router)
            logging.info("✅ router loaded: %s", module_name)
        except ModuleNotFoundError:
            logging.warning("↷ %s: module not found — skipped", module_name)
        except Exception:
            logging.exception("❌ router failed: %s", module_name)
            raise


# ── POLLING (worker) ─────────────────────────────────────────────────────────
async def run_polling() -> None:
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is required for polling mode")
    bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    await _include_routers(dp)
    logging.info("🚀 Start polling… [%s | %s | %s]", ENV, BUILD_MARK, SHORT_SHA[:7])
    await dp.start_polling(bot)


# ── FASTAPI: /status_json (web-only) ─────────────────────────────────────────
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


# ── FASTAPI: Webhook (Telegram → POST) ───────────────────────────────────────
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
        # Полная очистка любых «хвостов»
        await bot.delete_webhook(drop_pending_updates=True)
        await bot.set_webhook(
            url=url,
            secret_token=WEBHOOK_SECRET,
            drop_pending_updates=True,
            allowed_updates=["message", "callback_query"],
        )
        me = await bot.get_me()
        logging.info("✅ setWebhook: %s  (bot=%s @%s)", url, me.id, me.username)

    @app.on_event("shutdown")
    async def on_shutdown():
        await bot.session.close()

    @app.get("/status_json")
    async def status_json():
        try:
            me = await bot.get_me()
            bot_id = me.id
            bot_username = me.username
        except Exception:
            bot_id = None
            bot_username = None
        return {
            "build": BUILD_MARK,
            "sha": SHORT_SHA,
            "uptime_sec": _uptime_sec(),
            "env": ENV,
            "mode": "webhook",
            "bot_id": bot_id,
            "bot_username": bot_username,
        }

    @app.post(WEBHOOK_PATH)
    async def tg_webhook(request: Request) -> Response:
        # Проверяем секрет из заголовка
        if request.headers.get("X-Telegram-Bot-Api-Secret-Token") != WEBHOOK_SECRET:
            return Response(status_code=403)

        try:
            data = await request.json()
            update = Update.model_validate(data)
        except Exception:
            return Response(status_code=400)

        await dp.feed_update(bot, update)
        return Response(status_code=200)

    return app


# ── ENTRYPOINT (Render запускает через python -m app.main) ───────────────────
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
