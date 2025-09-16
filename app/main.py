# app/main.py
import os
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats
from aiogram.client.default import DefaultBotProperties

from app.config import settings
from app.middlewares.error_handler import ErrorsMiddleware
from app.storage.repo import init_db
from app.utils.maintenance import backup_sqlite, vacuum_sqlite

# === роутеры ===
from app.routers.onboarding import router as onboarding_router
from app.routers.menu import router as menu_router
from app.routers.training import router as training_router
from app.routers.casting import router as casting_router
from app.routers.progress import router as progress_router
from app.routers.coach import router as coach_router
from app.routers.settings import router as settings_router
from app.routers.admin import router as admin_router
from app.routers.premium import router as premium_router
from app.routers.deeplink import router as deeplink_router
from app.routers.feedback import router as feedback_router


def resolve_bot_token() -> str:
    """Берем токен из settings или ENV."""
    candidates_from_settings = [
        "BOT_TOKEN", "TG_BOT_TOKEN", "TELEGRAM_BOT_TOKEN", "TOKEN",
        "bot_token", "telegram_bot_token",
    ]
    for name in candidates_from_settings:
        if hasattr(settings, name):
            val = getattr(settings, name)
            if isinstance(val, str) and val.strip():
                return val.strip()

    for name in ["BOT_TOKEN", "TG_BOT_TOKEN", "TELEGRAM_BOT_TOKEN", "TOKEN"]:
        val = os.getenv(name)
        if isinstance(val, str) and val.strip():
            return val.strip()

    raise RuntimeError(
        "BOT token not found. Укажите settings.BOT_TOKEN или переменную окружения BOT_TOKEN."
    )


async def setup_commands(bot: Bot) -> None:
    cmds = [
        BotCommand(command="apply",     description="Путь лидера (заявка)"),
        BotCommand(command="training",  description="Тренировка дня"),
        BotCommand(command="casting",   description="Мини-кастинг"),
        BotCommand(command="progress",  description="Мой прогресс"),
        BotCommand(command="cancel",    description="Сбросить и открыть меню"),
        BotCommand(command="help",      description="Справка"),
        BotCommand(command="privacy",   description="Политика"),
        BotCommand(command="version",   description="Версия"),
        BotCommand(command="health",    description="Проверка статуса"),
    ]
    await bot.set_my_commands(cmds, scope=BotCommandScopeAllPrivateChats())


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    token = resolve_bot_token()

    # aiogram 3.7+: parse_mode задаем через default
    bot = Bot(token=token, default=DefaultBotProperties(parse_mode="HTML"))

    dp = Dispatcher(storage=MemoryStorage())
    dp.message.middleware(ErrorsMiddleware())

    # БД (СИНХРОННЫЙ вызов, без await)
    init_db()

    # Роутеры
    dp.include_router(onboarding_router)
    dp.include_router(menu_router)
    dp.include_router(training_router)
    dp.include_router(casting_router)
    dp.include_router(progress_router)
    dp.include_router(coach_router)
    dp.include_router(settings_router)
    dp.include_router(admin_router)
    dp.include_router(premium_router)
    dp.include_router(deeplink_router)
    dp.include_router(feedback_router)

    # Команды
    await setup_commands(bot)

    # Обслуживание SQLite (если функции синхронные — тоже без await)
    try:
        backup_sqlite()
        vacuum_sqlite()
    except Exception:
        # безопасно игнорируем на проде/postgres
        pass

    # Старт
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
