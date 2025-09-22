# app/main.py
from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from app.config import settings
from app.storage.repo import ensure_schema

# 👇 ЯВНЫЕ ИМПОРТЫ РОУТЕРОВ (порядок важен)
from app.routers import reply_shortcuts as r_short
from app.routers import deeplink as r_deeplink
from app.routers import training as r_training
from app.routers import casting as r_casting
from app.routers import progress as r_progress
from app.routers import apply as r_apply
from app.routers import privacy as r_privacy
from app.routers import help as r_help
from app.routers import settings as r_settings
from app.routers import cancel as r_cancel
# при необходимости добавляй остальные ниже (admin/analytics/feedback/shortcuts и т.д.)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("main")


async def _set_commands(bot: Bot) -> None:
    cmds = [
        BotCommand(command="start", description="Запуск / онбординг"),
        BotCommand(command="menu", description="Главное меню"),
        BotCommand(command="training", description="Тренировка дня"),
        BotCommand(command="casting", description="Мини-кастинг"),
        BotCommand(command="progress", description="Мой прогресс"),
        BotCommand(command="apply", description="Путь лидера"),
        BotCommand(command="privacy", description="Политика"),
        BotCommand(command="help", description="Помощь"),
        BotCommand(command="settings", description="Настройки"),
        BotCommand(command="cancel", description="Сбросить форму"),
    ]
    await bot.set_my_commands(cmds)


async def main() -> None:
    # 1) гарантируем схему БД (async)
    await ensure_schema()

    # 2) инициализация бота (aiogram 3.7+)
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    # 3) ПОДКЛЮЧЕНИЕ РОУТЕРОВ В НУЖНОМ ПОРЯДКЕ
    # самые первые — перехваты «🏠 В меню»/«Настройки»
    dp.include_router(r_short.router)
    # /start + диплинки
    dp.include_router(r_deeplink.router)
    # основные сценарии
    dp.include_router(r_training.router)
    dp.include_router(r_casting.router)
    dp.include_router(r_progress.router)
    dp.include_router(r_apply.router)
    dp.include_router(r_privacy.router)
    dp.include_router(r_help.router)
    dp.include_router(r_settings.router)
    dp.include_router(r_cancel.router)

    # 4) команды
    await _set_commands(bot)
    log.info("✅ Команды установлены")

    # 5) старт long polling
    log.info("🚀 Start polling…")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
