from __future__ import annotations

import asyncio
import logging
import os
from typing import Optional

from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Update

# подключаем ваши роутеры
from app.routers import hq_status  # <- этот файл выше

# ===== базовая конфигурация =====

BOT_TOKEN = os.environ["HQ_BOT_TOKEN"]  # у вас уже есть в env
WEBHOOK_BASE = os.getenv("WEBHOOK_URL_BASE")  # напр. https://elaya-stagecoach-web.onrender.com
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "/tg/webhook")
WEBHOOK_URL = (WEBHOOK_BASE + WEBHOOK_PATH) if WEBHOOK_BASE else None

# Важно: для групповых команд лучше сразу разрешить parse_mode=HTML
bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Подключаем роутеры
dp.include_router(hq_status.router)

app = FastAPI(title="Elaya Stagecoach — Webhook")


@app.get("/healthz")
async def healthz() -> dict:
    return {"status": "ok"}


@app.on_event("startup")
async def on_startup() -> None:
    logging.info("Starting FastAPI + Aiogram (webhook mode)")

    # Установим вебхук только если указан WEBHOOK_URL
    if WEBHOOK_URL:
        # Говорим Telegram слать только message-апдейты (вам этого сейчас достаточно)
        await bot.set_webhook(
            url=WEBHOOK_URL,
            allowed_updates=["message"],
            max_connections=40,
            drop_pending_updates=False,
        )
        logging.info("Webhook set to %s", WEBHOOK_URL)
    else:
        logging.warning("WEBHOOK_URL_BASE не задан — webhook не установлен")


@app.on_event("shutdown")
async def on_shutdown() -> None:
    # На Render это не обязательно, но аккуратно снять вебхук полезно.
    try:
        await bot.delete_webhook(drop_pending_updates=False)
    except Exception:  # noqa: BLE001
        pass
    await bot.session.close()


@app.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    """
    Единая точка входа для апдейтов от Telegram.
    """
    raw = await request.body()
    update = Update.model_validate_json(raw)
    await dp.feed_update(bot, update)
    return {"ok": True}
