import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from app.config import settings
from app.middlewares.error_handler import ErrorsMiddleware
from app.storage.repo import init_db

# ⚠️ Импортируем конкретно
from app.routers import onboarding
import app.routers.training as training
import app.routers.casting as casting
import app.routers.progress as progress
from app.routers import menu

logging.basicConfig(level=logging.INFO)

async def main():
    if not settings.bot_token:
        raise RuntimeError("BOT_TOKEN is empty. Set it in .env")
    init_db()

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher(storage=MemoryStorage())

    dp.message.middleware(ErrorsMiddleware())
    dp.callback_query.middleware(ErrorsMiddleware())

    # ⚠️ ВАЖНО: сначала «специализированные» роутеры, МЕНЮ — ПОСЛЕДНИМ
    dp.include_router(onboarding.router)
    dp.include_router(training.router)
    dp.include_router(casting.router)
    dp.include_router(progress.router)
    dp.include_router(menu.router)

    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == "__main__":
    asyncio.run(main())
