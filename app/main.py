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
from app.storage.mvp_repo import init_schema as init_mvp_schema
from app.routers.training import router as training_router
from app.routers.casting import router as casting_router
from app.routers.progress import router as progress_router
from app.utils.import_routers import import_and_collect_routers  # твой helper

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("main")


async def main() -> None:
    # База данных
    ensure_schema()       # базовые таблицы
    init_mvp_schema()     # дополнительные таблицы MVP

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    # Подключаем наши сценарии (MVP)
    dp.include_router(training_router)
    dp.include_router(casting_router)
    dp.include_router(progress_router)

    # Остальные роутеры через helper
    for r in import_and_collect_routers():
        dp.include_router(r)
        log.info("✅ Router '%s' подключён", r.name)

    # Команды в клиенте Telegram (меню слэшей)
    await bot.set_my_commands([
        BotCommand(command="start",    description="Начать / онбординг"),
        BotCommand(command="menu",     description="Открыть меню"),
        BotCommand(command="training", description="Тренировка"),
        BotCommand(command="casting",  description="Мини-кастинг"),
        BotCommand(command="progress", description="Мой прогресс"),
        BotCommand(command="apply",    description="Путь лидера (заявка)"),
        BotCommand(command="privacy",  description="Политика"),
        BotCommand(command="help",     description="Помощь"),
        BotCommand(command="settings", description="Настройки"),
        BotCommand(command="cancel",   description="Отмена"),
    ])
    log.info("✅ Команды установлены")
    log.info("🚀 Start polling…")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
