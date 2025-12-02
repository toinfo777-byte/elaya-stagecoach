from __future__ import annotations

import asyncio
import logging
import os
import uuid

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from app.config import settings
from app.routes import router as routes_router


# --- уникальный тег запуска (чтобы отличить в логах) ---
RUN_TAG = uuid.uuid4().hex[:8]

def _get_bot_token() -> str:
    return settings.tg_bot_token


async def heartbeat_loop(bot: Bot) -> None:
    """
    Каждые 30 секунд бот делает heartbeat в логах.
    Это покажет, КТО реально живой.
    """
    while True:
        try:
            me = await bot.get_me()
            logging.warning(f"[HEARTBEAT] bot={me.username}, tag={RUN_TAG}")
        except Exception as e:
            logging.error(f"[HEARTBEAT ERROR] {e}")
        await asyncio.sleep(30)


async def main() -> None:
    logging.warning("=== TRAINER STARTING ===")
    logging.warning(f"RUN_TAG = {RUN_TAG}")

    bot = Bot(token=_get_bot_token(), default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher()

    # добавляем роутеры
    dp.include_router(routes_router)

    # печатаем имя бота
    me = await bot.get_me()
    logging.warning(f"Trainer bot launched as @{me.username}, RUN_TAG={RUN_TAG}")

    # запускаем heartbeat
    asyncio.create_task(heartbeat_loop(bot))

    # стартуем
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
