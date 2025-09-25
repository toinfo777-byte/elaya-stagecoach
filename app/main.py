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

# ⬇️ ЯВНЫЕ ИМПОРТЫ РОУТЕРОВ
from app.routers import (
    start as r_start,
    common as r_common_guard,   # глобальный выход в меню (/menu, /start)
    help as r_help,
    privacy as r_privacy,
    progress as r_progress,
    settings as r_settings,
    extended as r_extended,
    training as r_training,
    entrypoints as r_entrypoints,   # 🔘 Кнопки нижнего меню (текстовые)
    casting as r_casting,       # анкета (P0 фикс портфолио включён)
    apply as r_apply,           # если используешь отдельный алиас
    minicasting as r_minicasting,  # 🎭 мини-кастинг (P1)
    leader as r_leader,            # 🧭 путь лидера (P1)
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
    # 1) гарантируем схему БД
    await ensure_schema()

    # 2) инициализация бота
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    # ⬅️ ВАЖНО: срезать «висячие» апдейты и убрать webHook
    await bot.delete_webhook(drop_pending_updates=True)

    # 3) ПОДКЛЮЧЕНИЕ РОУТЕРОВ (порядок ВАЖЕН!)
    # старт/диплинки
    dp.include_router(r_start.router)
    dp.include_router(r_entrypoints.router)  # текстовые кнопки меню, из любого состояния

    # СЦЕНАРИИ (FSM) — ставим ПЕРЕД common
    dp.include_router(r_minicasting.router)  # 🎭 Мини-кастинг
    dp.include_router(r_leader.router)       # 🧭 Путь лидера

    # guard — глобальный выход в меню/старт/отмена
    dp.include_router(r_common_guard.router)

    # ГЛОБАЛЬНЫЕ КОМАНДЫ
    dp.include_router(r_help.router)
    dp.include_router(r_privacy.router)
    dp.include_router(r_progress.router)
    dp.include_router(r_settings.router)
    dp.include_router(r_extended.router)

    # прочие сценарные роутеры
    dp.include_router(r_training.router)
    dp.include_router(r_casting.router)
    dp.include_router(r_apply.router)        # если используешь отдельный алиас

    # 4) команды
    await _set_commands(bot)
    log.info("✅ Команды установлены")

    # 5) старт long polling
    log.info("🚀 Start polling…")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
