from __future__ import annotations

import os
import logging
from typing import Any

from fastapi import FastAPI, Request, Response
from aiogram import Bot, Dispatcher
from aiogram.types import Update
from aiogram.enums import ParseMode

# Роутеры проекта
from app.routers import hq_status  # ← наш файл выше

# ─────────────────────────────────────────────────────────────────────────────
# ENV
# ─────────────────────────────────────────────────────────────────────────────
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN") or os.getenv("BOT_TOKEN") or ""
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN / TELEGRAM_TOKEN is not set")

ENV = os.getenv("ENV", os.getenv("ENVIRONMENT", "unknown"))
BUILD_MARK = os.getenv("BUILD_MARK", os.getenv("RENDER_GIT_COMMIT", "manual"))

# Фича-флаги
DISABLE_TG = os.getenv("DISABLE_TG", "0") == "1"
SEND_STARTUP_BANNER = os.getenv("SEND_STARTUP_BANNER", "0") == "1"

# ─────────────────────────────────────────────────────────────────────────────
# Core
# ─────────────────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("elaya.web")

bot = Bot(BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# Подключаем твои роутеры
dp.include_router(hq_status.router)

app = FastAPI(title="Elaya Stagecoach — Webhook")

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
        # Молча принимаем и игнорируем апдейт — бот «безмолвный»
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
    log.info("⚙️ Web app started | ENV=%s BUILD=%s", ENV, BUILD_MARK)

    if SEND_STARTUP_BANNER and not DISABLE_TG:
        try:
            # сюда можно подставить ID твоего HQ-чата/группы (env: HQ_CHAT_ID)
            chat_id = os.getenv("HQ_CHAT_ID")
            if chat_id:
                text = (
                    "🛰 <b>Штабной отчёт — Online</b>\n"
                    f"<code>env={ENV} build={BUILD_MARK}</code>\n"
                    "Webhook online; worker may be stopped."
                )
                await bot.send_message(chat_id, text)
        except Exception as e:
            log.warning("Startup banner error: %r", e)
