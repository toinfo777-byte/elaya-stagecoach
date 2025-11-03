# app/entrypoint_web.py
from __future__ import annotations

import asyncio
import json
import logging
import os
from typing import Optional

from fastapi import FastAPI, Request, HTTPException
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Update

# ⚙️ ваши конфиги
try:
    from app.config import settings  # у вас уже есть
    TG_TOKEN = settings.TG_BOT_TOKEN
    LOG_LEVEL = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
except Exception:
    TG_TOKEN = os.getenv("TG_BOT_TOKEN", "")
    LOG_LEVEL = getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO)

logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")
log = logging.getLogger("entrypoint_web")

# ⬇️ собираем ваши роутеры (оставь то, что реально используете сейчас)
from app.routers import (
    cmd_aliases,
    onboarding,
    system,
    help as help_router,
    minicasting,
    leader,
    training,
    progress,
    privacy,
    settings as settings_mod,
    extended,
    casting,
    apply,
    faq,
    devops_sync,
    panic,
)

# наш «универсальный» статус для приват/групп:
from app.routers.hq_status import router as hq_public_router


# --- core objects ---
app = FastAPI(title="Elaya Webhook")
bot = Bot(TG_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Подключаем роутеры бота
dp.include_router(help_router.router)
dp.include_router(cmd_aliases.router)
dp.include_router(onboarding.router)
dp.include_router(system.router)
dp.include_router(minicasting.router)
dp.include_router(leader.router)
dp.include_router(training.router)
dp.include_router(progress.router)
dp.include_router(privacy.router)
dp.include_router(settings_mod.router)
dp.include_router(extended.router)
dp.include_router(casting.router)
dp.include_router(apply.router)
dp.include_router(faq.router)
dp.include_router(devops_sync.router)
dp.include_router(panic.router)
dp.include_router(hq_public_router)  # наш статус-хендлер

# --- health ---
@app.get("/healthz")
async def healthz():
    loop = asyncio.get_event_loop()
    return {"ok": True, "uptime_s": int(loop.time())}

# --- webhook ---
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "/tg/webhook")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")  # опционально
ALLOWED_UPDATES = json.loads(os.getenv("ALLOWED_UPDATES", '["message"]'))

@app.post(WEBHOOK_PATH)
async def tg_webhook(request: Request):
    # (опционально) проверяем подпись/секрет
    if WEBHOOK_SECRET:
        if request.headers.get("X-Telegram-Bot-Api-Secret-Token") != WEBHOOK_SECRET:
            raise HTTPException(status_code=403, detail="Bad secret")
    data = await request.json()
    update = Update.model_validate(data)
    await dp.feed_update(bot, update)
    return {"ok": True}

# --- авто-установка webhook (по желанию через env) ---
@app.on_event("startup")
async def _set_webhook_on_start():
    auto = os.getenv("AUTO_SET_WEBHOOK", "0").lower() in {"1", "true", "yes"}
    base_url = os.getenv("PUBLIC_BASE_URL")  # например: https://elaya-stagecoach-web.onrender.com
    if not auto or not base_url:
        log.info("Webhook auto-set skipped (AUTO_SET_WEBHOOK=%s, PUBLIC_BASE_URL=%s)", auto, base_url)
        return

    url = base_url.rstrip("/") + WEBHOOK_PATH
    kwargs = {}
    if WEBHOOK_SECRET:
        kwargs["secret_token"] = WEBHOOK_SECRET
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_webhook(url=url, allowed_updates=ALLOWED_UPDATES, **kwargs)
    log.info("Webhook set to %s (allowed_updates=%s)", url, ALLOWED_UPDATES)
