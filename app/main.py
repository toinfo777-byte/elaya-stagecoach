# app/main.py
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats

from app.config import settings
from app.middlewares.error_handler import ErrorsMiddleware
from app.storage.repo import init_db

# Импорты роутеров
from app.routers.onboarding import router as onboarding_router
from app.routers.menu import router as menu_router
from app.routers.training import router as training_router
from app.routers.casting import router as casting_router
from app.routers.progress import router as progress_router
from app.routers.coach import router as coach_router
from app.routers.settings import router as settings_router
from app.routers.admin import router as admin_router
from app.routers.premium import router as premium_router
from app.routers.apply import router as apply_router
from app.routers.feedback import router as feedback_router
from app.routers.system import router as system_router
from app.routers.smoke import router as smoke_router   # ⬅️ новый

# если есть публикация постов
try:
    from app.routers.post import router as post_router
except Exception:
    post_router = None

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


# --- меню команд ---
async def setup_commands(bot: Bot) -> None:
    user_cmds = [
        BotCommand(command="start",       description="Начать"),
        BotCommand(command="apply",       description="Путь лидера (заявка)"),
        BotCommand(command="coach_on",    description="Включить наставника"),
        BotCommand(command="coach_off",   description="Выключить наставника"),
        BotCommand(command="ask",         description="Спросить наставника"),
        BotCommand(command="progress",    description="Мой прогресс"),  # ⬅️ добавили
        BotCommand(command="help",        description="Справка"),
        BotCommand(command="privacy",     description="Политика"),
    ]
    await bot.set_my_commands(user_cmds, scope=BotCommandScopeAllPrivateChats())


async def main():
    if not settings.bot_token:
        raise RuntimeError("BOT_TOKEN is empty")

    init_db()

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher(storage=MemoryStorage())

    # ошибки ловим в одном месте
    dp.message.middleware(ErrorsMiddleware())
    dp.callback_query.middleware(ErrorsMiddleware())

    # Подключаем ВСЕ роутеры
    for r in (
        smoke_router,     # ⬅️ первым
        apply_router,
        coach_router,
        onboarding_router,
        training_router,
        casting_router,
        progress_router,
        feedback_router,
        system_router,
        settings_router,
        admin_router,
        premium_router,
        menu_router,
    ):
        dp.include_router(r)
        log.info("Included router: %s", getattr(r, "name", r))

    if post_router:
        dp.include_router(post_router)
        log.info("Included router: %s", getattr(post_router, "name", post_router))

    async with bot:
        try:
            await bot.delete_webhook(drop_pending_updates=False)
        except Exception as e:
            log.warning("delete_webhook failed: %s", e)

        try:
            await setup_commands(bot)
        except Exception as e:
            log.warning("setup_commands failed: %s", e)

        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
