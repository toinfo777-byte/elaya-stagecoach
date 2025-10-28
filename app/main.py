# app/main.py
from __future__ import annotations

import asyncio
import hashlib
import importlib
import logging
import os
import sys
import time
from typing import Any

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import BotCommand
from fastapi import FastAPI

from app.build import BUILD_MARK
from app.config import settings
from app.storage.repo import ensure_schema

# Роутеры бота
from app.routers import (
    entrypoints,
    help,
    cmd_aliases,
    onboarding,
    system,
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
    hq,  # HQ-репорт
    diag,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(settings.TG_BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Регистрация роутеров
for router in [
    entrypoints.router,
    help.router,
    cmd_aliases.router,
    onboarding.router,
    system.router,
    minicasting.router,
    leader.router,
    training.router,
    progress.router,
    privacy.router,
    settings_mod.router,
    extended.router,
    casting.router,
    apply.router,
    faq.router,
    devops_sync.router,
    panic.router,
    hq.router,
    diag.router,
]:
    dp.include_router(router)

# Команды
async def set_bot_commands():
    commands = [
        BotCommand(command="menu", description="Главное меню"),
        BotCommand(command="help", description="Помощь и FAQ"),
    ]
    try:
        await bot.set_my_commands(commands)
    except TelegramBadRequest as e:
        logger.warning(f"Failed to set commands: {e}")

# Основной запуск
async def main():
    await ensure_schema()
    await set_bot_commands()
    logger.info(f"🚀 Elaya StageCoach started | Build: {BUILD_MARK}")
    await dp.start_polling(bot)

# FastAPI для Render web endpoint
app = FastAPI()

@app.get("/")
async def root() -> dict[str, Any]:
    return {"status": "ok", "build": BUILD_MARK}

if __name__ == "__main__":
    asyncio.run(main())
