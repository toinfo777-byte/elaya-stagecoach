from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.config import settings
from app.storage.repo import ensure_schema
from app.utils.import_routers import import_and_collect_routers  # если есть у тебя хелпер; иначе подключай вручную

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("main")


async def main() -> None:
    # гарантируем схему БД
    ensure_schema()

    # aiogram 3.7+: parse_mode через DefaultBotProperties
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    # Подключаем роутеры (или подключи вручную)
    for r in import_and_collect_routers():
        dp.include_router(r)
        log.info("✅ Router '%s' подключён", r.name)

    log.info("✅ Команды установлены")
    log.info("🚀 Start polling…")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
