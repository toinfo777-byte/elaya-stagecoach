# app/main.py
from __future__ import annotations

import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

# ===== РОУТЕРЫ (важен порядок!)
from app.routers.smoke import router as smoke_router          # /ping, /health
from app.routers.apply import router as apply_router          # заявка (Путь лидера)
from app.routers.deeplink import router as deeplink_router    # /start <payload>
from app.routers.shortcuts import router as shortcuts_router  # /training, /casting, кнопки в любом состоянии
from app.routers.reply_shortcuts import router as reply_shortcuts_router  # если есть
from app.routers.onboarding import router as onboarding_router            # /start
from app.routers.training import router as training_router
from app.routers.casting import router as casting_router
from app.routers.progress import router as progress_router
from app.bot.handlers.feedback import router as feedback2_router          # 🔥/👌/😐 и ✍ 1 фраза
from app.routers.system import router as system_router
from app.routers.settings import router as settings_router
from app.routers.admin import router as admin_router
from app.routers.premium import router as premium_router
from app.routers.metrics import router as metrics_router
from app.routers.cancel import router as cancel_router
from app.routers.menu import router as menu_router

# База (если у вас sync SQLAlchemy — НЕ await)
from app.storage.repo import init_db

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN")


async def main() -> None:
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is not set")

    # aiogram 3.7+: parse_mode через DefaultBotProperties
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode="HTML"),
    )
    dp = Dispatcher(storage=MemoryStorage())

    # БД (синхронная инициализация — без await)
    try:
        init_db()
    except Exception as e:
        logging.exception("init_db error: %s", e)

    # ПОДКЛЮЧАЕМ РОУТЕРЫ В ЖЕСТКО ЗАДАННОМ ПОРЯДКЕ
    # 1) всегда-ловящие команды/кнопки
    dp.include_router(smoke_router)
    dp.include_router(deeplink_router)         # обрабатывает /start payload
    dp.include_router(shortcuts_router)        # /training, /casting, «Мой прогресс», кнопки меню

    # 2) профильные сценарии
    dp.include_router(onboarding_router)       # обычный /start (анкета)
    dp.include_router(training_router)
    dp.include_router(casting_router)
    dp.include_router(apply_router)

    # 3) фидбек (эмодзи и «1 фраза»)
    dp.include_router(feedback2_router)

    # 4) прочее
    dp.include_router(progress_router)
    dp.include_router(settings_router)
    dp.include_router(system_router)
    dp.include_router(admin_router)
    dp.include_router(premium_router)
    dp.include_router(metrics_router)
    dp.include_router(cancel_router)

    # 5) всегда последним — меню (клавиатура)
    dp.include_router(menu_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
