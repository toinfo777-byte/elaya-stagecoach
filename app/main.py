from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.config import settings
from app.storage.repo import ensure_schema

# ← Роутеры подключаем руками
from app.routers import (
    reply_shortcuts,
    cancel,
    onboarding,
    menu,
    training,
    casting,
    apply,
    progress,
    settings as settings_router,  # чтобы не конфликтовать с app.config.settings
    analytics,
    # feedback,  # если сломан — оставь закомментированным
)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("main")


async def main() -> None:
    # Гарантир
