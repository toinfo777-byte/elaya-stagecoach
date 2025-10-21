from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from app.config import settings
from app.storage.repo import ensure_schema

# === Подключаем ТОЛЬКО новые роутеры из этого патча ===
from app.routers.entrypoints import router as go_router   # единый вход / меню / алиасы
from app.routers.help import help_router                  # /help + меню/политика/настройки
from app.routers.training import tr_router                # тренировки
from app.routers.minicasting import mc_router             # мини-кастинг
from app.routers.leader import leader_router              # путь лидера
from app.routers.progress import progress_router          # прогресс

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
    # 1) схема БД
    await ensure_schema()

    # 2) бот/DP
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    # 3) снять webhook и дропнуть «висячие» апдейты (анти-конфликт polling)
    await bot.delete_webhook(drop_pending_updates=True)
    log.info("Webhook deleted, pending updates dropped")

    # 4) порядок важен: сначала вход/алиасы, затем разделы
    dp.include_routers(
        go_router,
        help_router,
        tr_router,
        mc_router,
        leader_router,
        progress_router,
    )

    # 5) команды
    await _set_commands(bot)
    log.info("✅ Команды установлены")

    # 6) polling
    log.info("🚀 Start polling…")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
