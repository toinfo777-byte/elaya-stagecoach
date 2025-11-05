from __future__ import annotations

import os
import time
import logging
from typing import Any, Optional

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration

from fastapi import FastAPI, Request, Response
from aiogram import Bot, Dispatcher
from aiogram.types import Update
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

# Роутеры проекта
from app.routers import hq_status  # ваш существующий router

# ─────────────────────────────────────────────────────────────────────────────
# ENV / Settings
# ─────────────────────────────────────────────────────────────────────────────
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN") or os.getenv("BOT_TOKEN") or ""
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN / TELEGRAM_TOKEN is not set")

ENV = os.getenv("ENV", os.getenv("ENVIRONMENT", "unknown"))
BUILD_MARK = os.getenv("BUILD_MARK", os.getenv("RENDER_GIT_COMMIT", "manual"))

# Фича-флаги и мониторинг
DISABLE_TG = os.getenv("DISABLE_TG", "0") == "1"
SEND_STARTUP_BANNER = os.getenv("SEND_STARTUP_BANNER", "0") == "1"

SENTRY_DSN = os.getenv("SENTRY_DSN")  # ← прокидываем в Render/GitHub
SENTRY_ENV = os.getenv("SENTRY_ENV", ENV)
SENTRY_TRACES_SAMPLE_RATE = float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.0"))

ADMIN_ALERT_CHAT_ID: Optional[int] = None
if os.getenv("ADMIN_ALERT_CHAT_ID"):
    # id может быть отрицательным (супергруппа) — это ок
    ADMIN_ALERT_CHAT_ID = int(os.getenv("ADMIN_ALERT_CHAT_ID"))

ALERT_COOLDOWN_SEC = int(os.getenv("ALERT_COOLDOWN_SEC", "120"))  # анти-спам алёртов
_last_alert_ts = 0.0

# ─────────────────────────────────────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("elaya.web")

# ─────────────────────────────────────────────────────────────────────────────
# Sentry
# ─────────────────────────────────────────────────────────────────────────────
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        environment=SENTRY_ENV,
        traces_sample_rate=SENTRY_TRACES_SAMPLE_RATE,
        integrations=[
            LoggingIntegration(level=logging.INFO, event_level=logging.ERROR),
            StarletteIntegration(transaction_style="url"),
        ],
        send_default_pii=False,
    )
    log.info("Sentry initialized, env=%s rate=%s", SENTRY_ENV, SENTRY_TRACES_SAMPLE_RATE)
else:
    log.info("Sentry disabled (no SENTRY_DSN)")

# ─────────────────────────────────────────────────────────────────────────────
# Telegram core
# ─────────────────────────────────────────────────────────────────────────────
bot = Bot(
    BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
dp = Dispatcher()
dp.include_router(hq_status.router)

app = FastAPI(title="Elaya Stagecoach — Webhook")

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────
async def safe_admin_alert(text: str) -> None:
    """
    Безопасная отправка админ-алёрта в Telegram.
    С анти-спамом и подавлением исключений (чтобы не циклило падения).
    """
    global _last_alert_ts
    if DISABLE_TG or ADMIN_ALERT_CHAT_ID is None:
        return
    now = time.time()
    if now - _last_alert_ts < ALERT_COOLDOWN_SEC:
        return
    _last_alert_ts = now
    try:
        await bot.send_message(ADMIN_ALERT_CHAT_ID, text)
    except Exception as e:
        log.warning("admin alert failed: %r", e)

# ─────────────────────────────────────────────────────────────────────────────
# Health
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/healthz")
async def healthz() -> dict[str, Any]:
    return {"ok": True, "env": ENV, "build": BUILD_MARK}

@app.get("/")
async def root() -> dict[str, Any]:
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
        # Логируем, шлём в Sentry и уведомляем админов
        log.exception("Webhook handler error")
        if SENTRY_DSN:
            sentry_sdk.capture_exception(e)

        await safe_admin_alert(
            "⚠️ <b>Webhook error</b>\n"
            f"<code>env={ENV} build={BUILD_MARK}</code>\n"
            f"Exception: <code>{type(e).__name__}</code>"
        )
        # Telegram ждёт 200/4xx/5xx — вернём 200, чтобы не засорять pending_update_count
        return Response(status_code=200)

# ─────────────────────────────────────────────────────────────────────────────
# Startup / Shutdown
# ─────────────────────────────────────────────────────────────────────────────
@app.on_event("startup")
async def on_startup() -> None:
    log.info("⚙️ Web app started | ENV=%s BUILD=%s", ENV, BUILD_MARK)
    if SEND_STARTUP_BANNER and not DISABLE_TG:
        await safe_admin_alert(
            "🛰 <b>Штабной отчёт — Online</b>\n"
            f"<code>env={ENV} build={BUILD_MARK}</code>\n"
            "Webhook online; worker may be stopped."
        )

@app.on_event("shutdown")
async def on_shutdown() -> None:
    log.info("🛑 Web app stopped | ENV=%s BUILD=%s", ENV, BUILD_MARK)
