from __future__ import annotations

import os
import logging

from fastapi import FastAPI, Request, Response
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Update

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.asyncio import AsyncioIntegration

from app.routers import hq as hq_router  # этот файл из блока выше

# ─────────────────────────────────────────────────────────────────────────────
# ENV & logging
# ─────────────────────────────────────────────────────────────────────────────
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN") or os.getenv("BOT_TOKEN") or ""
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN / TELEGRAM_TOKEN is not set")

ENV = os.getenv("ENV", os.getenv("ENVIRONMENT", "unknown"))
BUILD_MARK = os.getenv("BUILD_MARK", os.getenv("RENDER_GIT_COMMIT", "manual"))

ADMIN_ALERT_CHAT_ID = os.getenv("ADMIN_ALERT_CHAT_ID")  # можно -100... для супергруппы
HQ_CHAT_ID = os.getenv("HQ_CHAT_ID") or os.getenv("TG_HQ_CHAT_ID")

DISABLE_TG = os.getenv("DISABLE_TG", "0") == "1"
SEND_STARTUP_BANNER = os.getenv("SEND_STARTUP_BANNER", "1") == "1"

SENTRY_DSN = os.getenv("SENTRY_DSN")

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("elaya.web")

# ─────────────────────────────────────────────────────────────────────────────
# Sentry
# ─────────────────────────────────────────────────────────────────────────────
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        environment=ENV,
        release=BUILD_MARK,
        integrations=[FastApiIntegration(), AsyncioIntegration()],
        traces_sample_rate=0.05,
    )
    log.info("Sentry initialized")

# ─────────────────────────────────────────────────────────────────────────────
# Aiogram core
# ─────────────────────────────────────────────────────────────────────────────
bot = Bot(
    BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
dp = Dispatcher()
dp.include_router(hq_router.router)

app = FastAPI(title="Elaya Stagecoach — Webhook")

# ─────────────────────────────────────────────────────────────────────────────
# Small helpers
# ─────────────────────────────────────────────────────────────────────────────
async def _admin_alert(text: str) -> None:
    if not ADMIN_ALERT_CHAT_ID:
        return
    try:
        await bot.send_message(int(ADMIN_ALERT_CHAT_ID), f"🚨 <b>Webhook alert</b>\n{text}")
    except Exception as e:
        log.warning("Failed to send admin alert: %r", e)

# ─────────────────────────────────────────────────────────────────────────────
# Health
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/healthz")
async def healthz() -> dict:
    return {"ok": True, "env": ENV, "build": BUILD_MARK}

@app.get("/")
async def root() -> dict:
    return {"ok": True, "service": "elaya-stagecoach-web", "mode": "webhook"}

# ─────────────────────────────────────────────────────────────────────────────
# Telegram Webhook
# ─────────────────────────────────────────────────────────────────────────────
@app.post("/tg/webhook")
async def tg_webhook(request: Request) -> Response:
    if DISABLE_TG:
        return Response(status_code=200)

    try:
        data = await request.json()
        update = Update.model_validate(data)
        await dp.feed_update(bot, update)
        return Response(status_code=200)
    except Exception as e:
        # ловим любые падения обработчика апдейтов
        log.exception("Webhook error")
        if SENTRY_DSN:
            sentry_sdk.capture_exception(e)
        await _admin_alert(f"env={ENV} build={BUILD_MARK}\n{e!r}")
        # 200, чтобы Telegram не зафлудил ретраями; ошибка уже зафиксирована
        return Response(status_code=200)

# ─────────────────────────────────────────────────────────────────────────────
# Startup hook
# ─────────────────────────────────────────────────────────────────────────────
@app.on_event("startup")
async def on_startup() -> None:
    log.info("⚙️ Web app started | ENV=%s BUILD=%s", ENV, BUILD_MARK)

    # стартовый отчёт только один раз (анти-дубликат внутри send_hq_report)
    if SEND_STARTUP_BANNER and not DISABLE_TG and HQ_CHAT_ID:
        try:
            await hq_router.send_hq_report(
                bot=bot,
                chat_id=int(HQ_CHAT_ID),
                state="Online",
            )
        except Exception as e:
            log.warning("Startup banner error: %r", e)
