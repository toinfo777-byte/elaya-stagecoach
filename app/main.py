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

# ⬇️ ЯВНЫЕ ИМПОРТЫ РОУТЕРОВ (как просили)
from app.routers import (
    start as r_start,
    common as r_common_guard,
    help as r_help,
    extended as r_extended,
    settings as r_settings,
    casting as r_casting,
    apply as r_apply,
    training as r_training,
    progress as r_progress,
    privacy as r_privacy,
)

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
        BotCommand(command="extended", description="Расширенная версия"),
        BotCommand(command="help", description="Помощь"),
        BotCommand(command="settings", description="Настройки"),
        BotCommand(command="cancel", description="Сбросить форму"),
    ]
    await bot.set_my_commands(cmds)


async def main() -> None:
    # 1) гарантируем схему БД (async)
    await ensure_schema()

    # 2) инициализация бота
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    # 3) ПОДКЛЮЧЕНИЕ РОУТЕРОВ (порядок ВАЖЕН!)
    # старт и диплинки
    dp.include_router(r_start.router)

    # guard — раньше всех командных роутеров
    dp.include_router(r_common_guard.router)

    # основные разделы/сценарии
    dp.include_router(r_training.router)
    dp.include_router(r_progress.router)
    dp.include_router(r_casting.router)
    dp.include_router(r_apply.router)
    dp.include_router(r_privacy.router)
    dp.include_router(r_help.router)
    dp.include_router(r_extended.router)
    dp.include_router(r_settings.router)

    # 4) команды
    await _set_commands(bot)
    log.info("✅ Команды установлены")

    # 5) старт long polling
    log.info("🚀 Start polling…")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
