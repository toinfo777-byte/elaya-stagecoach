from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from app.config import settings
from app.storage.repo import ensure_schema
from app.routers.training import router as training_router
from app.routers.casting import router as casting_router
from app.routers.onboarding import router as onboarding_router
from app.routers.reply_shortcuts import router as reply_shortcuts_router
from app.routers.menu import router as menu_router
from app.routers.progress import router as progress_router
from app.routers.apply import router as apply_router
from app.routers.settings import router as settings_router
from app.routers.cancel import router as cancel_router
from app.routers.analytics import router as analytics_router

log = logging.getLogger("main")
logging.basicConfig(level=logging.INFO)

async def set_commands(bot: Bot) -> None:
    await bot.set_my_commands([
        BotCommand(command="start", description="Начать / онбординг"),
        BotCommand(command="menu", description="Открыть меню"),
        BotCommand(command="training", description="Тренировка"),
        BotCommand(command="casting", description="Мини-кастинг"),
        BotCommand(command="progress", description="Мой прогресс"),
        BotCommand(command="apply", description="Путь лидера"),
        BotCommand(command="privacy", description="Политика"),
        BotCommand(command="settings", description="Настройки"),
        BotCommand(command="help", description="Помощь"),
        BotCommand(command="cancel", description="Отмена"),
    ])

async def main() -> None:
    ensure_schema()

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    # ВАЖНО: сначала роутеры для deeplink,
    # затем всё остальное и общий /start без payload
    dp.include_routers(
        training_router,
        casting_router,
        onboarding_router,        # /start без payload
        reply_shortcuts_router,
        menu_router,
        progress_router,
        apply_router,
        settings_router,
        cancel_router,
        analytics_router,
    )

    await set_commands(bot)
    log.info("🚀 Start polling…")
    await dp.start_polling(bot, allowed_updates=["message", "callback_query"])

if __name__ == "__main__":
    asyncio.run(main())
