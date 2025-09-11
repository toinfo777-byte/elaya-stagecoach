# app/main.py
import asyncio
import logging
from datetime import datetime, timedelta, timezone

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats

from app.config import settings
from app.middlewares.error_handler import ErrorsMiddleware
from app.middlewares.source_tags import SourceTagsMiddleware
from app.storage.repo import init_db

# ===== РОУТЕРЫ (явные импорты и порядок важен) =====
from app.routers.smoke import router as smoke_router               # /ping, /health
from app.routers.apply import router as apply_router               # заявка
from app.routers.deeplink import router as deeplink_router         # диплинки /start <payload>
from app.routers.shortcuts import router as shortcuts_router       # шорткаты (/training, /casting, кнопки) В ЛЮБОМ состоянии
from app.routers.onboarding import router as onboarding_router     # онбординг (/start)
from app.routers.coach import router as coach_router               # наставник
from app.routers.training import router as training_router         # тренировка
from app.routers.casting import router as casting_router           # мини-кастинг
from app.routers.progress import router as progress_router         # прогресс
from app.routers.feedback import router as feedback_router         # отзывы (и метрика feedback_added)
from app.routers.system import router as system_router             # /help, /privacy, /whoami, /version, /health
from app.routers.settings import router as settings_router         # тех.настройки
from app.routers.admin import router as admin_router               # админка
from app.routers.premium import router as premium_router           # плата/заглушки
from app.routers.metrics import router as metrics_router           # ✅ /metrics (админы)
from app.routers.cancel import router as cancel_router             # глобальная отмена /cancel
from app.routers.menu import router as menu_router                 # меню (всегда последним)

# ⬇️ НОВОЕ: универсальный обработчик отзывов (кнопки 🔥/👌/😐 + «1 фраза»)
from app.bot.handlers.feedback import router as feedback2_router

# Обслуживание SQLite
from app.utils.maintenance import backup_sqlite, vacuum_sqlite

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
log = logging.getLogger(__name__)


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


# ====== меню команд ======
async def setup_commands(bot: Bot) -> None:
    user_cmds = [
        BotCommand(command="start",     description="Начать"),
        BotCommand(command="apply",     description="Путь лидера (заявка)"),
        BotCommand(command="coach_on",  description="Включить наставника"),
        BotCommand(command="coach_off", description="Выключить наставника"),
        BotCommand(command="ask",       description="Спросить наставника"),
        BotCommand(command="training",  description="Тренировка дня"),
        BotCommand(command="casting",   description="Мини-кастинг"),
        BotCommand(command="progress",  description="Мой прогресс"),
        BotCommand(command="cancel",    description="Сбросить и открыть меню"),
        BotCommand(command="help",      description="Справка"),
        BotCommand(command="privacy",   description="Политика"),
        BotCommand(command="version",   description="Версия"),
    ]
    await bot.set_my_commands(user_cmds, scope=BotCommandScopeAllPrivateChats())


# ====== main ======
async def main():
    if not settings.bot_token:
        raise RuntimeError("BOT_TOKEN is empty. Set it in .env")

    init_db()

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher(storage=MemoryStorage())

    # middlewares
    dp.message.middleware(SourceTagsMiddleware())      # источник first/last_source
    dp.callback_query.middleware(SourceTagsMiddleware())
    dp.message.middleware(ErrorsMiddleware())          # единый перехват ошибок
    dp.callback_query.middleware(ErrorsMiddleware())

    # ПОРЯДОК ВАЖЕН!
    for r in (
        smoke_router,        # быстрые проверки
        apply_router,
        deeplink_router,     # диплинки должны идти РАНО
        shortcuts_router,    # /training, /casting и кнопки — в любом состоянии
        onboarding_router,   # /start попадает сюда раньше coach
        coach_router,
        training_router,
        casting_router,
        progress_router,

        # наш новый обработчик отзывов (кнопки 🔥/👌/😐 + «1 фраза»)
        feedback2_router,

        # существующий проектный роутер отзывов (если есть своя метрика/логика)
        feedback_router,

        system_router,
        settings_router,
        admin_router,
        premium_router,
        metrics_router,      # ✅ метрики до cancel/menu
        cancel_router,       # глобальная отмена до меню
        menu_router,         # меню — строго последним
    ):
        dp.include_router(r)
        log.info("Included router: %s", getattr(r, "name", r))

    async with bot:
        try:
            await bot.delete_webhook(drop_pending_updates=False)
        except Exception as e:
            log.warning("delete_webhook failed: %s", e)

        try:
            await setup_commands(bot)
        except Exception as e:
            log.warning("setup_commands failed: %s", e)

        # фоновые задачи
        asyncio.create_task(_backup_loop())
        asyncio.create_task(_vacuum_loop())

        await dp.start_polling(
            bot,
            allowed_updates=dp.resolve_used_update_types(),
            polling_timeout=30,
        )


if __name__ == "__main__":
    asyncio.run(main())
