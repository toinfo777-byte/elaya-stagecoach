from __future__ import annotations

import logging
import os
from importlib import import_module
from typing import Any

import sentry_sdk
from fastapi import FastAPI, Request, Response
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramAPIError
from aiogram.types import Update

# ─────────────────────────────────────────────────────────────────────────────
# ENV / Config
# ─────────────────────────────────────────────────────────────────────────────

def getenv_bool(key: str, default: str = "0") -> bool:
    return (os.getenv(key, default) or "").strip() in {"1", "true", "True", "yes", "on"}

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN") or os.getenv("BOT_TOKEN") or os.getenv("TG_BOT_TOKEN") or ""
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN / TELEGRAM_TOKEN is not set (trainer)")

ENV = os.getenv("ENV", os.getenv("ENVIRONMENT", "unknown"))
BUILD_MARK = os.getenv("BUILD_MARK", os.getenv("RENDER_GIT_COMMIT", "manual"))

SENTRY_DSN = os.getenv("SENTRY_DSN", "")
ADMIN_ALERT_CHAT_ID = os.getenv("ADMIN_ALERT_CHAT_ID", "")

DISABLE_TG = getenv_bool("DISABLE_TG", "0")
SEND_STARTUP_BANNER = getenv_bool("SEND_STARTUP_BANNER", "0")
BANNER_CHAT_ID = os.getenv("HQ_CHAT_ID") or os.getenv("TRAINER_BANNER_CHAT_ID", "")

# ─────────────────────────────────────────────────────────────────────────────
# Logging & Sentry
# ─────────────────────────────────────────────────────────────────────────────

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("elaya.trainer")

if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
    )
    log.info("Sentry initialized (trainer)")

# ─────────────────────────────────────────────────────────────────────────────
# Bot / Dispatcher
# ─────────────────────────────────────────────────────────────────────────────

bot = Bot(
    BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
dp = Dispatcher()


def include_optional_router(module_path: str, attr: str = "router") -> None:
    try:
        m = import_module(module_path)
        router = getattr(m, attr, None)
        if router is not None:
            dp.include_router(router)
            log.info("Router loaded: %s.%s", module_path, attr)
    except Exception as e:  # noqa: BLE001
        log.info("Router skipped: %s (%r)", module_path, e)


# Подключаем «тренерские» роутеры (безопасные попытки)
include_optional_router("app.routers.training")
include_optional_router("app.routers.progress")
include_optional_router("app.routers.settings")
include_optional_router("app.routers.entrypoints")
include_optional_router("app.routers.system")

# ─────────────────────────────────────────────────────────────────────────────
# FastAPI app
# ─────────────────────────────────────────────────────────────────────────────

app = FastAPI(title="Elaya Trainer Bot — Webhook")


@app.get("/healthz")
async def healthz() -> dict[str, Any]:
    return {"ok": True, "env": ENV, "build": BUILD_MARK, "webhook": (not DISABLE_TG)}


@app.get("/")
async def root() -> dict[str, Any]:
    return {"ok": True, "service": "elaya-trainer-bot", "mode": "webhook"}


async def notify_admin(text: str) -> None:
    if not ADMIN_ALERT_CHAT_ID:
        return
    try:
        await bot.send_message(int(ADMIN_ALERT_CHAT_ID), f"🚨 <b>{text}</b>")
    except TelegramAPIError:
        pass


@app.post("/tg/webhook")
async def tg_webhook(request: Request) -> Response:
    if DISABLE_TG:
        return Response(status_code=200)

    try:
        data = await request.json()
        update = Update.model_validate(data)
        await dp.feed_update(bot, update)
    except Exception as e:  # noqa: BLE001
        log.exception("Trainer webhook error")
        if SENTRY_DSN:
            sentry_sdk.capture_exception(e)
        await notify_admin(f"Trainer webhook error: {type(e).__name__}")
    return Response(status_code=200)


@app.on_event("startup")
async def on_startup() -> None:
    log.info("🏋️ Trainer web app started | ENV=%s BUILD=%s", ENV, BUILD_MARK)

    if SEND_STARTUP_BANNER and not DISABLE_TG and BANNER_CHAT_ID:
        try:
            await bot.send_message(
                int(BANNER_CHAT_ID),
                "🏋️ <b>Trainer online</b>\n"
                f"<code>env={ENV} build={BUILD_MARK}</code>\n"
                "Webhook online; worker may be stopped.",
            )
        except Exception as e:  # noqa: BLE001
            log.warning("Startup banner error (trainer): %r", e)
            if SENTRY_DSN:
                sentry_sdk.capture_exception(e)
