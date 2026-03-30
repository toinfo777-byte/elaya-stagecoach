from __future__ import annotations

import asyncio
import logging
import uuid

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from app.config import settings
from app.routes import router as routes_router

logger = logging.getLogger(__name__)


def _get_bot_token() -> str:
    return settings.tg_bot_token


async def main() -> None:
    logging.warning("=== TRAINER STARTING ===")

    run_id = uuid.uuid4().hex[:6]
    logging.warning("🚨 TRAINER RUN_ID=%s", run_id)

    bot = Bot(
        token=_get_bot_token(),
        default=DefaultBotProperties(parse_mode="HTML"),
    )

    dp = Dispatcher()

    # Подключаем только ОДИН агрегированный router
    dp.include_router(routes_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
