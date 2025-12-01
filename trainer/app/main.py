# trainer/app/main.py
from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from app.config import settings
from app.routes import router as routes_router

# --- ЯВНАЯ ЗАГРУЗКА trainer/.env -----------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent  # .../trainer
env_path = BASE_DIR / ".env"
load_dotenv(env_path)


def _get_bot_token() -> str:
    return settings.tg_bot_token


async def main() -> None:
    bot = Bot(token=_get_bot_token(), default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher()

    dp.include_router(routes_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
