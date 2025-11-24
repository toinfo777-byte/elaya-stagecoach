# trainer/app/main.py
from __future__ import annotations

import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from app.routes import menu, training


def _get_bot_token() -> str:
    """
    Ищем токен тренер-бота в нескольких переменных окружения.
    Можно использовать любую из них на Render.
    """
    for name in ("TRAINER_BOT_TOKEN", "BOT_TOKEN", "TELEGRAM_BOT_TOKEN"):
        token = os.getenv(name, "").strip()
        if token:
            return token
    raise RuntimeError(
        "Trainer bot token is not set. "
        "Set TRAINER_BOT_TOKEN (или BOT_TOKEN / TELEGRAM_BOT_TOKEN) в переменных окружения."
    )


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    bot_token = _get_bot_token()

    bot = Bot(
        token=bot_token,
        default=DefaultBotProperties(parse_mode="HTML"),
    )
    dp = Dispatcher()

    # --- подключаем роутеры тренера ---
    dp.include_router(menu.router)
    dp.include_router(training.router)

    # --- стартуем ---
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
