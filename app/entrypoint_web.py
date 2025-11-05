from __future__ import annotations

import os
import logging
from typing import Any

from fastapi import FastAPI, Request, Response
from aiogram import Bot, Dispatcher
from aiogram.types import Update
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from app.routers import hq_status  # наш HQ-роутер

# ─────────────────────────────────────────────────────────────────────────────
# ENV
# ─────────────────────────────────────────────────────────────────────────────
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN") or os.getenv("BOT_TOKEN") or ""
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN / TELEGRAM_TOKEN is not set")

ENV = os.getenv("ENV", os.getenv("ENVIRONMENT", "unknown"))
BUILD_MARK = os.getenv("BUILD_MARK", os.getenv("RENDER_GIT_COMMIT", "manual"))

# Render context (если есть)
RENDER_SERVICE = os.getenv("RENDER_SERVICE_NAME", os.getenv("RENDER_SERVICE", ""))
RENDER_INSTANCE = os.getenv("RENDER_INSTANCE_ID", "")
RENDER_REGION = os.getenv("RENDER_REGION", "")

# Фича-флаги
DISABLE_TG = os.getenv("DISABLE_TG", "0") == "1"
SEND_STARTUP_BANNER = os.getenv("SEND_STARTUP_BANNER", "0") == "1"

# Admin/HQ
HQ_CHAT_ID = os.getenv("HQ_CHAT_ID") or os.getenv("TG_HQ_CHAT_ID")
ADMIN_ALERT_CHAT_ID = os.getenv("ADMIN_ALERT_CHAT_ID") or os.getenv("TG_REPORT_CHAT_ID")

# ─────────────────────────────────────────────────────────────────────────────
# Core
# ─────────────────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("elaya.web")

bot = Bot(
    BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
dp = Dispatcher()
dp.include_router(hq_status.router)

app = FastAPI(title="Elaya Stagecoach — Webhook")

# ─────────────────────────────────────────────────────────────────────────────
# Health
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/healthz")
async def healthz() -> dict[str, Any]:
    return {
        "ok": True,
        "env": ENV,
        "build": BUILD_MARK,
        "service": RENDER_SERVICE,
        "instance": RENDER_INSTANCE,
        "region": RENDER_REGION,
    }


@app.get("/")
async def root() -> dict[str, Any]:
    return {
        "ok": True,
        "service": "elaya-stagecoach-web",
        "mode": "webhook",
        "env": ENV,
    }

# ─────────────────────────────────────────────────────────────────────────────
# Telegram Webhook
# ─────────────────────────────────────────────────────────────────────────────
@app.post("/tg/webhook")
async def tg_webhook(request: Request) -> Response:
    if DISABLE_TG:
        return Response(status_code=200)

    data = await request.json()
    update = Update.model_validate(data)
    await dp.feed_update(bot, update)
    return Response(status_code=200)

# ─────────────────────────────────────────────────────────────────────────────
# Startup hook
# ─────────────────────────────────────────────────────────────────────────────
@app.on_event("startup")
async def on_startup() -> None:
    log.info(
        "⚙️ Web app started | ENV=%s BUILD=%s SERVICE=%s INSTANCE=%s REGION=%s",
        ENV, BUILD_MARK, RENDER_SERVICE, RENDER_INSTANCE, RENDER_REGION,
    )

    if SEND_STARTUP_BANNER and not DISABLE_TG and HQ_CHAT_ID:
        try:
            text = (
                "🛰 <b>Штабной отчёт — Online</b>\n"
                f"<code>env={ENV} build={BUILD_MARK}</code>\n"
                f"service=<code>{RENDER_SERVICE or '—'}</code> "
                f"instance=<code>{RENDER_INSTANCE or '—'}</code> "
                f"region=<code>{RENDER_REGION or '—'}</code>\n"
                "Webhook online; worker may be stopped."
            )
            await bot.send_message(HQ_CHAT_ID, text)
        except Exception as e:
            log.warning("Startup banner error: %r", e)
