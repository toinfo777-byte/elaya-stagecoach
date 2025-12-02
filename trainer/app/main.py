from __future__ import annotations
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from app.config import settings
from app.routes import router as training_router


async def main() -> None:
    bot = Bot(
        token=settings.tg_bot_token,
        default=DefaultBotProperties(parse_mode="HTML")
    )
    dp = Dispatcher()
    dp.include_router(training_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
