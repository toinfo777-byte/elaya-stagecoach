from __future__ import annotations

import asyncio
import hashlib
import logging
import importlib
import sys
import time

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import BotCommand

from fastapi import FastAPI

from app.config import settings
from app.build import BUILD_MARK
from app.storage.repo import ensure_schema

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
    hq,     # добавлен HQ-роутер
    panic,
    diag,   # health/diag/status_json
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("main")

START_TIME = time.time()


async def _set_commands(bot: Bot) -> None:
    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Запуск / меню"),
            BotCommand(command="menu", description="Главное меню"),
            BotCommand(command="levels", description="Тренировка дня"),
            BotCommand(command="progress", description="Мой прогресс"),
            BotCommand(command="help", description="Помощь / FAQ"),
            BotCommand(command="ping", description="Проверка связи"),
            BotCommand(command="hq", description="HQ-сводка"),  # новое
        ]
    )


async def _guard(coro, what: str):
    try:
        return await coro
    except TelegramBadRequest as e:
        if "Logged out" in str(e):
            log.warning("%s: Bot API 'Logged out' — игнорируем", what)
            return
        raise


async def _get_status_dict() -> dict:
    uptime = int(time.time() - START_TIME)
    return {
        "build": BUILD_MARK,
        "sha": settings.build_sha or "unknown",
        "uptime_sec": uptime,
        "env": settings.env,
        "mode": settings.mode,
        "bot_id": settings.bot_id or None,
    }


# ───────────────────────── Polling mode (bot) ─────────────────────────
async def run_polling() -> None_
