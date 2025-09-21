from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from app.config import settings
from app.storage.repo import ensure_schema
from app.utils.import_routers import import_and_collect_routers  # твой helper

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("main")

async def main() -> None:
    ensure_schema()

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    # Роутеры
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
