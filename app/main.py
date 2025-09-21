from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.config import settings
from app.storage.repo import ensure_schema

# Роутеры подключаем вручную
from app.routers import (
    reply_shortcuts,
    cancel,
    onboarding,
    menu,
    training,
    casting,
    apply,
    progress,
    settings as settings_router,  # не конфликтуем с app.config.settings
    analytics,
    # feedback,  # если этот модуль у тебя ещё не готов — оставь закомментированным
)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("main")


async def main() -> None:
    # Гарантируем, что БД инициализирована
    ensure_schema()

    # aiogram 3.7+: parse_mode через DefaultBotProperties
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    # Подключаем роутеры
    dp.include_router(reply_shortcuts.router)
    dp.include_router(cancel.router)
    dp.include_router(onboarding.router)
    dp.include_router(menu.router)
    dp.include_router(training.router)
    dp.include_router(casting.router)
    dp.include_router(apply.router)
    dp.include_router(progress.router)
    dp.include_router(settings_router.router)
    dp.include_router(analytics.router)
    # dp.include_router(feedback.router)

    log.info("🚀 Start polling…")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
