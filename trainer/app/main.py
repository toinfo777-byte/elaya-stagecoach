from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from app.config import settings
from app.routes import router as routes_router


logging.basicConfig(level=logging.INFO)


def _get_bot_token() -> str:
    return settings.tg_bot_token


async def main() -> None:
    bot = Bot(
        token=_get_bot_token(),
        default=DefaultBotProperties(parse_mode="HTML"),
    )
    dp = Dispatcher()

    # Подключаем агрегированный роутер
    dp.include_router(routes_router)

    logging.warning("=== TRAINER STARTING ===")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
