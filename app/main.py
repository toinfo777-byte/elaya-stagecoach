# app/main.py
import asyncio
import logging
from datetime import datetime, timedelta, timezone

from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage

from app.config import settings
from app.middlewares.error_handler import ErrorsMiddleware
from app.middlewares.source_tags import SourceTagsMiddleware
from app.storage.repo import init_db

# ===== РОУТЕРЫ =====
from app.routers.smoke import router as smoke_router
from app.routers.apply import router as apply_router
from app.routers.deeplink import router as deeplink_router
from app.routers.shortcuts import router as shortcuts_router
from app.routers.onboarding import router as onboarding_router
from app.routers.coach import router as coach_router
from app.routers.training import router as training_router
from app.routers.casting import router as casting_router
from app.routers.progress import router as progress_router
from app.routers.feedback import router as feedback_router
from app.routers.system import router as system_router
from app.routers.settings import router as settings_router
from app.routers.admin import router as admin_router
from app.routers.premium import router as premium_router
from app.routers.metrics import router as metrics_router
from app.routers.cancel import router as cancel_router
from app.routers.menu import router as menu_router

# новый универсальный обработчик отзывов (кнопки 🔥/👌/😐 + «1 фраза»)
from app.bot.handlers.feedback import router as feedback2_router

# диагностический роутер (только логирование апдейтов)
from app.routers.debug import router as debug_router

# Обслуживание SQLite
from app.utils.maintenance import backup_sqlite, vacuum_sqlite

# ========= ЛОГИ =========
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
log = logging.getLogger(__name__)
logging.getLogger("aiogram").setLevel(logging.DEBUG)  # детальные логи апдейтов

# ====== фоновые задачи обслуживания БД ======
async def _sleep_until_utc(hour: int, minute: int = 0, dow: int | None = None):
    now = datetime.now(timezone.utc).replace(second=0, microsecond=0)
    target = now.replace(hour=hour, minute=minute)
    if target <= now:
        target += timedelta(days=1)
    if dow is not None:
        while target.weekday() != dow:
            target += timedelta(days=1)
    await asyncio.sleep((target - now).total_seconds())

async def _backup_loop():
    while True:
        await _sleep_until_utc(2, 0)  # ежедневно 02:00 UTC
        try:
            path = backup_sqlite()
            log.info("Backup done: %s", path)
        except Exception as e:
            log.exception("Backup failed: %s", e)

async def _vacuum_loop():
    while True:
        await _sleep_until_utc(2, 5, dow=6)  # вс 02:05 UTC
        try:
            vacuum_sqlite()
            log.info("Vacuum done")
        except Exception as e:
            log.exception("Vacuum failed: %s", e)

# (опционально) установка /команд — отключено, чтобы не мешало запуску
async def setup_commands(bot: Bot) -> None:
    try:
        commands: list[types.BotCommand] = [
            types.BotCommand(command="start",     description="Начать"),
            types.BotCommand(command="apply",     description="Путь лидера (заявка)"),
            types.BotCommand(command="coach_on",  description="Включить наставника"),
            types.BotCommand(command="coach_off", description="Выключить наставника"),
            types.BotCommand(command="ask",       description="Спросить наставника"),
            types.BotCommand(command="training",  description="Тренировка дня"),
            types.BotCommand(command="casting",   description="Мини-кастинг"),
            types.BotCommand(command="progress",  description="Мой прогресс"),
            types.BotCommand(command="cancel",    description="Сбросить и открыть меню"),
            types.BotCommand(command="help",      description="Справка"),
            types.BotCommand(command="privacy",   description="Политика"),
            types.BotCommand(command="version",   description="Версия"),
        ]
        await bot.set_my_commands(
            commands=commands,
            scope=types.BotCommandScopeAllPrivateChats(),
        )
        log.info("Bot commands set successfully")
    except Exception as e:
        log.warning("setup_commands failed: %s", e)

# ====== main ======
async def main():
    if not settings.bot_token:
        raise RuntimeError("BOT_TOKEN is empty. Set it in .env")

    init_db()

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher(storage=MemoryStorage())

    # middlewares
    dp.message.middleware(SourceTagsMiddleware())
    dp.callback_query.middleware(SourceTagsMiddleware())
    dp.message.middleware(ErrorsMiddleware())
    dp.callback_query.middleware(ErrorsMiddleware())

    # ПОРЯДОК ВАЖЕН!
    for r in (
        smoke_router,
        apply_router,
        deeplink_router,
        shortcuts_router,
        onboarding_router,
        coach_router,
        training_router,
        casting_router,
        progress_router,

        feedback2_router,    # новый обработчик отзывов
        feedback_router,     # проектный (если есть своя логика/метрики)

        system_router,
        settings_router,
        admin_router,
        premium_router,
        metrics_router,
        cancel_router,

        debug_router,        # <— логируем любые апдейты, оставить перед меню
        menu_router,         # меню — строго последним
    ):
        dp.include_router(r)
        log.info("Included router: %s", getattr(r, "name", r))

    async with bot:
        try:
            await bot.delete_webhook(drop_pending_updates=False)
        except Exception as e:
            log.warning("delete_webhook failed: %s", e)

        # Оставляем выключенным ради стабильности
        # await setup_commands(bot)

        # фоновые задачи
        asyncio.create_task(_backup_loop())
        asyncio.create_task(_vacuum_loop())

        await dp.start_polling(
            bot,
            allowed_updates=None,  # забираем вообще все типы апдейтов
            polling_timeout=30,
        )

if __name__ == "__main__":
    asyncio.run(main())
