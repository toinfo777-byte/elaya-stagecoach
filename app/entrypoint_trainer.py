from __future__ import annotations

import logging
import os

from fastapi import FastAPI, Request, HTTPException
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Update

from app.config import settings
from app.build import BUILD_MARK
from app.routers import start as start_router
from app.routers import menu, help, policy, progress, reviews, apply as apply_router

# --- токен и секрет ---

BOT_TOKEN = (
    os.getenv("TG_BOT_TOKEN", "").strip()
    or (settings.tg_bot_token or "")  # TELEGRAM_TOKEN
    or (settings.bot_token or "")     # BOT_TOKEN
)
if not BOT_TOKEN:
    raise RuntimeError("TG_BOT_TOKEN / TELEGRAM_TOKEN / BOT_TOKEN is not set")

WEBHOOK_SECRET = (
    os.getenv("TG_WEBHOOK_SECRET", "").strip()
    or (settings.webhook_secret or "")
)

# --- aiogram core ---

bot = Bot(
    BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
dp = Dispatcher()

for r in (
    start_router.router,
    menu.router,
    help.router,
    policy.router,
    progress.router,
    reviews.router,
    apply_router.router,
):
    dp.include_router(r)

# --- FastAPI app ---

app = FastAPI(title="Elaya Trainer — webhook")


@app.on_event("startup")
async def on_startup() -> None:
    log_level = getattr(settings, "log_level", "INFO")
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO)
    )
    me = await bot.get_me()
    logging.info(
        ">>> Startup (trainer): id=%s user=@%s build=%s",
        me.id,
        me.username,
        settings.build_mark or BUILD_MARK,
    )


@app.get("/healthz")
async def healthz():
    return {"ok": True}


@app.post("/tg/webhook")
async de
