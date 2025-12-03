from __future__ import annotations

import asyncio
import logging
import uuid

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from app.config import settings
from app.routes import router as routes_router
from app.core_client import send_timeline_event  # <- добавили

# Тег запуска, чтобы отличать экземпляры в логах
RUN_TAG = uuid.uuid4().hex[:8]


class TelegramConflictFilter(logging.Filter):
    """
    Фильтр, который вырезает TelegramConflictError из логгера aiogram.dispatcher,
    чтобы при деплое лог не был полностью красным.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        msg = record.getMessage()
        return "TelegramConflictError" not in msg


def _get_bot_token() -> str:
    token = settings.tg_bot_token
    if not token:
        raise RuntimeError("TG_BOT_TOKEN is empty")
    return token


async def heartbeat_loop(bot: Bot) -> None:
    """
    Периодический heartbeat, чтобы видеть, какой именно экземпляр бота живой.
    """
    while True:
        try:
            me = await bot.get_me()
            logging.warning(f"[HEARTBEAT] bot={me.username}, tag={RUN_TAG}")
        except Exception as e:
            logging.error(f"[HEARTBEAT ERROR] {e}")
        await asyncio.sleep(30)


async def main() -> None:
    # Базовая настройка логов
    logging.basicConfig(level=logging.INFO)

    # Приглушаем именно dispatcher-логгер
    dlogger = logging.getLogger("aiogram.dispatcher")
    dlogger.addFilter(TelegramConflictFilter())

    logging.warning("=== TRAINER STARTING ===")
    logging.warning(f"RUN_TAG = {RUN_TAG}")

    bot = Bot(
        token=_get_bot_token(),
        default=DefaultBotProperties(parse_mode="HTML"),
    )
    dp = Dispatcher()

    # Подключаем агрегированный роутер
    dp.include_router(routes_router)

    me = await bot.get_me()
    logging.warning(f"Trainer bot launched as @{me.username}, RUN_TAG={RUN_TAG}")

    # Отправляем событие в ядро: тренер вышел в эфир
    try:
        asyncio.create_task(
            send_timeline_event(
                scene="trainer_online",
                payload={"run_tag": RUN_TAG},
            )
        )
    except Exception as e:
        logging.error("Failed to schedule trainer_online event: %s", e)

    # Запускаем heartbeat
    asyncio.create_task(heartbeat_loop(bot))

    # Стартуем polling
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
