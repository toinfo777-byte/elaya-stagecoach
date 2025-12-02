from __future__ import annotations

import asyncio
import logging
import uuid

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.exceptions import TelegramConflictError

from app.config import settings
from app.routes import router as routes_router


logger = logging.getLogger(__name__)


def _get_bot_token() -> str:
    """
    Берём токен тренера из настроек.
    Если токен не задан — сразу падаем, чтобы это было видно.
    """
    token = settings.tg_bot_token
    if not token:
        raise RuntimeError("TG_BOT_TOKEN is not set in settings")
    return token


async def main() -> None:
    # Базовая настройка логирования
    logging.basicConfig(level=logging.INFO)

    # УНИКАЛЬНЫЙ UID запуска тренера — чтобы видеть, кто именно поднялся
    startup_uid = uuid.uuid4().hex[:8]
    logger.warning("🚨 TRAINER BOT ONLINE — UID: %s", startup_uid)

    # Логируем префикс токена, чтобы различать, какой именно токен используется
    token = _get_bot_token()
    logger.warning("🚨 Trainer starting with token prefix: %s…", token[:10])

    # Стартуем бота
    bot = Bot(token=token, default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher()

    # Подключаем агрегированный роутер тренера
    dp.include_router(routes_router)

    try:
        await dp.start_polling(bot)
    except TelegramConflictError:
        logger.error("❌ TELEGRAM CONFLICT: second bot instance detected for this token")
        # Пробрасываем дальше, чтобы в логах Render было видно падение
        raise


if __name__ == "__main__":
    asyncio.run(main())
