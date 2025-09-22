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

# 👇 ЯВНЫЕ ИМПОРТЫ РОУТЕРОВ (именно подмодули)
from app.routers.reply_shortcuts import router as reply_shortcuts_router
from app.routers.deeplink import router as deeplink_router

from app.routers.training import router as training_router
from app.routers.casting import router as casting_router
from app.routers.progress import router as progress_router
from app.routers.apply import router as apply_router
from app.routers.privacy import router as privacy_router
from app.routers.extended import router as extended_router
from app.routers.help import router as help_router
from app.routers.settings import router as settings_router
from app.routers.cancel import router as cancel_router

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
    # --- ГЛОБАЛЬНЫЕ ШОРТКАТЫ (первыми, чтобы ловить из любого state) ---
    dp.include_router(reply_shortcuts_router)

    # --- ДИПЛИНКИ (/start с payload) ---
    dp.include_router(deeplink_router)

    # --- ОСНОВНЫЕ СЦЕНАРИИ ---
    dp.include_router(training_router)
    dp.include_router(casting_router)
    dp.include_router(progress_router)
    dp.include_router(apply_router)
    dp.include_router(privacy_router)
    dp.include_router(extended_router)
    dp.include_router(help_router)
    dp.include_router(settings_router)
    dp.include_router(cancel_router)

    # 4) команды
    await _set_commands(bot)
    log.info("✅ Команды установлены")

    # 5) старт long polling
    log.info("🚀 Start polling…")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
