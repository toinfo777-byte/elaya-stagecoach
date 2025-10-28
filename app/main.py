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

# ------------------------- env helpers -------------------------

def env(name: str, default: str = "") -> str:
    val = os.getenv(name)
    return (val if val is not None else default).strip()

MODE: str = env("MODE", "worker")           # worker | web | webhook
ENV: str = env("ENV", "develop")

# Токен бота: допускаем альтернативное имя переменной для совместимости
BOT_TOKEN: str = env("BOT_TOKEN") or env("TELEGRAM_TOKEN") or env("TELEGRAM_TOKEN_PROD")

# Параметры вебхука (используются только в MODE=webhook)
WEBHOOK_BASE: str = env("WEBHOOK_BASE")     # например, https://elaya-stagecoach-web.onrender.com
WEBHOOK_PATH: str = env("WEBHOOK_PATH")     # например, /tg/<секрет>
WEBHOOK_SECRET: str = env("WEBHOOK_SECRET") # тот же <секрет> для заголовка

# Служебные метки сборки
BUILD_MARK: str = env("BUILD_MARK", env("BUILD_SHA", "local"))
SHORT_SHA: str = env("SHORT_SHA", env("BUILD_SHA", "local")[:7])

# Render прокидывает PORT — используем его, иначе 8000
PORT: int = int(env("PORT", "8000"))

# ------------------------- logging -------------------------

logging.basicConfig(
    level=getattr(logging, env("LOG_LEVEL", "INFO"), logging.INFO),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
log = logging.getLogger("elaya.main")

START_TS = time.time()


# ------------------------- routers loader -------------------------

def _iter_router_modules() -> Iterable[str]:
    """
    Список потенциальных роутеров. Отсутствующие — просто пропускаем с warning.
    Подставь сюда свои реальные файлы из app/routers/.
    """
    return (
        "app.routers.system",
        "app.routers.hq",
        # "app.routers.help",
        # "app.routers.onboarding",
        # "app.routers.training",
        # и т.д.
    )


async def include_known_routers(dp: Dispatcher) -> None:
    for module_name in _iter_router_modules():
        try:
            mod = import_module(module_name)
            router = getattr(mod, "router")
            dp.include_router(router)
            log.info("✅ router loaded: %s", module_name)
        except ModuleNotFoundError:
            log.warning("⚠️  router module not found: %s (skipped)", module_name)
        except AttributeError:
            log.warning("⚠️  no `router` in module: %s (skipped)", module_name)
        except Exception:
            log.exception("❌ router import failed: %s", module_name)
            # не валим приложение — продолжаем


# ------------------------- status helpers -------------------------

def uptime_sec() -> int:
    return int(time.time() - START_TS)


# ------------------------- worker (polling) -------------------------

async def run_polling() -> None:
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is required for polling mode")

    bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    await include_known_routers(dp)

    me = await bot.get_me()
    log.info("🚀 Start polling… env=%s mode=worker build=%s sha=%s bot@%s id=%s",
             ENV, BUILD_MARK, SHORT_SHA, me.username, me.id)

    await dp.start_polling(bot)


# ------------------------- web (status only) -------------------------

def build_status_app() -> FastAPI:
    app = FastAPI(title="Elaya StageCoach (status)", version=BUILD_MARK)

    @app.get("/status_json")
    async def status_json():
        return {
            "build": BUILD_MARK,
            "sha": SHORT_SHA,
            "uptime_sec": uptime_sec(),
            "env": ENV,
            "mode": "web",
            "bot_id": None,
        }

    @app.get("/healthz")
    async def healthz():
        return {"ok": True}

    return app


# ------------------------- webhook (Telegram push) -------------------------

def build_webhook_app() -> FastAPI:
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is required for webhook mode")
    if not (WEBHOOK_BASE and WEBHOOK_PATH and WEBHOOK_SECRET):
        raise RuntimeError("WEBHOOK_BASE/WEBHOOK_PATH/WEBHOOK_SECRET are required for webhook mode")

    bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    app = FastAPI(title="Elaya StageCoach (webhook)", version=BUILD_MARK)

    @app.on_event("startup")
    async def _startup():
        await include_known_routers(dp)
        url = f"{WEBHOOK_BASE}{WEBHOOK_PATH}"

        # На всякий случай чистим прежний вебхук и дропаем хвосты
        await bot.delete_webhook(drop_pending_updates=True)
        await bot.set_webhook(
            url=url,
            secret_token=WEBHOOK_SECRET,
            drop_pending_updates=True,
        )
        me = await bot.get_me()
        log.info("✅ setWebhook: %s | bot@%s id=%s | env=%s build=%s",
                 url, me.username, me.id, ENV, BUILD_MARK)

    @app.on_event("shutdown")
    async def _shutdown():
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
            "uptime_sec": uptime_sec(),
            "env": ENV,
            "mode": "webhook",
            "bot_id": getattr(me, "id", None),
            "bot_username": getattr(me, "username", None),
        }

    @app.get("/healthz")
    async def healthz():
        return {"ok": True}

    @app.post(WEBHOOK_PATH)
    async def tg_webhook(request: Request) -> Response:
        # Мини-проверка секрета
        if request.headers.get("X-Telegram-Bot-Api-Secret-Token") != WEBHOOK_SECRET:
            return Response(status_code=403)

        data = await request.json()
        try:
            update = Update.model_validate(data)  # aiogram v3 / pydantic v2
        except Exception:
            return Response(status_code=400)

        await dp.feed_update(bot, update)
        return Response(status_code=200)

    return app


# ------------------------- entrypoint -------------------------

if __name__ == "__main__":
    import uvicorn

    if MODE == "worker":
        asyncio.run(run_polling())

    elif MODE == "web":
        # только статус
        uvicorn.run(build_status_app, host="0.0.0.0", port=PORT, factory=True)

    elif MODE == "webhook":
        # приём апдейтов от Telegram
        uvicorn.run(build_webhook_app, host="0.0.0.0", port=PORT, factory=True)

    else:
        raise RuntimeError(f"Unknown MODE: {MODE}")
