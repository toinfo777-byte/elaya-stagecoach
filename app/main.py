# app/main.py
from __future__ import annotations

import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Update
from fastapi import FastAPI, Request, HTTPException
from starlette.responses import PlainTextResponse

from app.config import settings
from app.build import BUILD_MARK

# ── FastAPI (web) ─────────────────────────────────────────────────────────────
app = FastAPI()
dp = Dispatcher()

BOT_PROFILE = os.getenv("BOT_PROFILE", "hq").strip().lower()
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "").strip()

# Роутеры подключаем БЕЗ сайд-эффектов
from app.routers import system, hq  # базовые штабные
dp.include_router(system.router)
dp.include_router(hq.router)

if BOT_PROFILE == "trainer":
    from app.routers import trainer  # фронтовой контур
    dp.include_router(trainer.router)

@app.get("/healthz")
async def healthz():
    return PlainTextResponse("ok")

@app.post("/tg/webhook")
async def tg_webhook(request: Request):
    # Проверка секрета вебхука (советую оставить включённой)
    secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
    if WEBHOOK_SECRET and secret != WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail="bad webhook secret")
    body = await request.body()
    try:
        update = Update.model_validate_json(body)
    except Exception as e:
        logging.exception("Webhook: bad update: %s", e)
        raise HTTPException(status_code=400, detail="bad update")
    bot: Bot = request.app.state.bot
    await dp.feed_update(bot, update)
    return PlainTextResponse("ok")

# ── Startup/Shutdown ──────────────────────────────────────────────────────────
async def _on_startup(bot: Bot):
    me = await bot.get_me()
    logging.info(">>> Startup: %s as @%s | profile=%s | build=%s",
                 me.id, me.username, BOT_PROFILE, BUILD_MARK)

async def _ensure_webhook(bot: Bot):
    """
    Ставит вебхук на https://<service>.onrender.com/tg/webhook с секретом.
    """
    base_url = os.getenv("RENDER_EXTERNAL_URL") or os.getenv("SERVICE_URL") \
               or os.getenv("STAGECOACH_WEB_URL") or ""
    # Для trainer-бота правильный домен — самого сервиса, где он запущен:
    # Render сам прокидывает внешний URL в переменную RENDER_EXTERNAL_URL на старте контейнера.
    if not base_url:
        # Фоллбек: явно собрать из env, если задано вручную.
        base_url = f"https://{os.getenv('RENDER_SERVICE_HOST', '').strip()}"
    # На Render домен вида https://<service>.onrender.com уже в RENDER_EXTERNAL_URL.
    webhook_url = (base_url.rstrip("/")) + "/tg/webhook"

    current = await bot.get_webhook_info()
    if current.url != webhook_url:
        await bot.set_webhook(
            url=webhook_url,
            secret_token=WEBHOOK_SECRET or None,
            drop_pending_updates=False,
            allowed_updates=["message", "callback_query"]
        )
        logging.info("Webhook set to %s", webhook_url)
    else:
        logging.info("Webhook already set: %s", webhook_url)

@app.on_event("startup")
async def on_startup():
    logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))

    token = (
        settings.TG_BOT_TOKEN
        or settings.BOT_TOKEN
        or os.getenv("TELEGRAM_TOKEN")
        or os.getenv("BOT_TOKEN")
    )
    if not token:
        raise RuntimeError("TELEGRAM_TOKEN / BOT_TOKEN is not set")

    bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    app.state.bot = bot

    await _on_startup(bot)
    await _ensure_webhook(bot)

@app.on_event("shutdown")
async def on_shutdown():
    bot: Bot | None = getattr(app.state, "bot", None)
    if bot:
        await bot.session.close()
    logging.info(">>> Shutdown clean")
