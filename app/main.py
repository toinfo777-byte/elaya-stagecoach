# app/main.py
from __future__ import annotations

import asyncio
import logging
from contextlib import suppress

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.utils.config import settings
from app.storage.repo import init_db  # синхронная инициализация
from app.middlewares.error_handler import ErrorsMiddleware
from app.middlewares.source_tags import SourceTagsMiddleware

# ==== РОУТЕРЫ (очевидные импорты и порядок важен) ====
from app.routers.smoke import router as smoke_router              # /ping, /health
from app.routers.apply import router as apply_router              # заявка (Путь лидера)
from app.routers.deeplink import router as deeplink_router        # диплинки /start <payload>
from app.routers.shortcuts import router as shortcuts_router      # /training, /casting, кнопки (в любом состоянии)
from app.routers.reply_shortcuts import router as reply_shortcuts_router
from app.routers.onboarding import router as onboarding_router    # /start
from app.routers.coach import router as coach_router              # наставник (если есть — можно отключить)
from app.routers.training import router as training_router        # тренировка
from app.routers.casting import router as casting_router          # мини-кастинг
from app.routers.progress import router as progress_router        # прогресс
# старый проектный фидбек можно не подключать
from app.bot.handlers.feedback import router as feedback2_router  # 🔥/👌/😐 и ✍️ 1 фраза (универсально)
from app.routers.system import router as system_router            # /help, /privacy, /whoami, /version, /health
from app.routers.settings import router as settings_router        # тех.настройки
from app.routers.admin import router as admin_router              # админка
from app.routers.premium import router as premium_router          # плата/заглушки
from app.routers.metrics import router as metrics_router          # /metrics (админы)
from app.routers.cancel import router as cancel_router            # глобальная отмена /cancel
from app.routers.menu import router as menu_router                # меню (строго последним)

logging.basicConfig(level=logging.INFO)

async def main() -> None:
    # ---- init DB (синхронная функция) ----
    # внутри init_db() делается engine/metadata.create_all(...) без await
    init_db()

    # ---- bot/dispatcher ----
    token = settings.bot_token  # см. utils/config.py ниже
    bot = Bot(
        token=token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    # ---- middlewares ----
    dp.update.middleware(ErrorsMiddleware())
    dp.update.middleware(SourceTagsMiddleware())

    # ---- routers ----
    dp.include_router(smoke_router)
    dp.include_router(apply_router)
    dp.include_router(deeplink_router)
    dp.include_router(shortcuts_router)
    dp.include_router(reply_shortcuts_router)
    dp.include_router(onboarding_router)
    dp.include_router(coach_router)
    dp.include_router(training_router)
    dp.include_router(casting_router)
    dp.include_router(progress_router)
    dp.include_router(feedback2_router)  # универсальный обработчик отзывов
    dp.include_router(system_router)
    dp.include_router(settings_router)
    dp.include_router(admin_router)
    dp.include_router(premium_router)
    dp.include_router(metrics_router)
    dp.include_router(cancel_router)
    dp.include_router(menu_router)

    # ---- start polling ----
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == "__main__":
    with suppress(KeyboardInterrupt):
        asyncio.run(main())
