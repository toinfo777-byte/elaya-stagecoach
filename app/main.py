from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from app.config import settings
from app.storage.repo import ensure_schema

# ——— РОУТЕРЫ ———
from app.routers.entrypoints import go_router            # единый вход: /menu, /training, go:* и т.п.
from app.routers.help import help_router                 # /help + меню/политика/настройки
from app.routers.training import router as tr_router     # тренировка дня (если у вас другой экспорт — поправьте)
from app.routers.minicasting import mc_router            # мини-кастинг (mc_router должен существовать)
from app.routers.leader import router as leader_router   # путь лидера
from app.routers.progress import router as progress_router
from app.routers.privacy import router as privacy_router
from app.routers.settings import router as settings_router
from app.routers.extended import router as extended_router
# при необходимости: from app.routers.start import router as start_router

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

    # 3) срезать webhook и висячие апдейты (анти-конфликт polling)
    await bot.delete_webhook(drop_pending_updates=True)

    # 4) порядок подключения (важен!)
    dp.include_routers(
        go_router,         # ← ПЕРВЫМ: ловит /menu, /training, go:* из любого состояния
        help_router,       # /help и базовые экраны
        tr_router,         # тренировки
        mc_router,         # мини-кастинг
        leader_router,     # путь лидера
        progress_router,   # прогресс
        privacy_router,    # политика
        settings_router,   # настройки
        extended_router,   # расширенная версия
        # start_router,    # если используете отдельный /start с диплинками
    )

    # 5) команды
    await _set_commands(bot)
    log.info("✅ Команды установлены")

    # 6) polling
    log.info("🚀 Start polling…")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
