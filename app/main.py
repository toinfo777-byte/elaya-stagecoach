# app/main.py
import asyncio
import logging
from datetime import datetime, timedelta, timezone

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats

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


# ====== меню команд ======
async def setup_commands(bot: Bot) -> None:
    cmds = [
        BotCommand(command="start",     description="Начать"),
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


# ====== основной запуск ======
async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    bot = Bot(token=settings.BOT_TOKEN, parse_mode="HTML")
    dp = Dispatcher(storage=MemoryStorage())
    dp.message.middleware(ErrorsMiddleware())

    # init db
    await init_db()

    # регистрируем роутеры
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

    # ставим команды
    await setup_commands(bot)

    # техобслуживание БД
    await backup_sqlite()
    await vacuum_sqlite()

    # стартуем
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
