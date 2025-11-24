# trainer/app/main.py
from __future__ import annotations

import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from app.routes import router as routes_router


def _get_bot_token() -> str:
    """
    Ищем токен тренер-бота в нескольких переменных окружения.
    """
    for name in ("TRAINER_BOT_TOKEN", "BOT_TOKEN", "TELEGRAM_BOT_TOKEN"):
        token = os.getenv(name, "").strip()
        if token:
            return token
    raise RuntimeError(
        "Trainer bot token is not set. "
        "Set TRAINER_BOT_TOKEN (или BOT_TOKEN / TELEGRAM_BOT_TOKEN)."
    )


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    bot_token = _get_bot_token()

    bot = Bot(
        token=bot_token,
        default=DefaultBotProperties(parse_mode="HTML"),
    )
    dp = Dispatcher()

    # --- подключаем все роутеры тренера через routes.__init__ ---
    dp.include_router(routes_router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
