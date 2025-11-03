# app/entrypoint_worker.py
from __future__ import annotations

import asyncio
import logging
import os
from datetime import datetime, timedelta, timezone

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

try:
    from app.config import settings
    TG_TOKEN = settings.TG_BOT_TOKEN
    LOG_LEVEL = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
except Exception:
    TG_TOKEN = os.getenv("TG_BOT_TOKEN", "")
    LOG_LEVEL = getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO)

logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")
log = logging.getLogger("entrypoint_worker")

# Параметры расписания
TZ_OFFSET_HOURS = int(os.getenv("TZ_OFFSET_HOURS", "3"))  # МСК по умолчанию
RUN_AT_HOUR = int(os.getenv("NIGHTLY_HOUR", "23"))
RUN_AT_MIN = int(os.getenv("NIGHTLY_MINUTE", "59"))
CHANNEL_ID = int(os.getenv("HQ_CHANNEL_ID", "0"))  # укажи ID канала (со знаком минус)

bot = Bot(TG_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


def _next_run(now: datetime) -> datetime:
    """Ближайшее время запуска (сегодня 23:59 или завтра)."""
    target = now.replace(hour=RUN_AT_HOUR, minute=RUN_AT_MIN, second=0, microsecond=0)
    if target <= now:
        target += timedelta(days=1)
    return target


async def nightly_loop() -> None:
    from app.jobs.nightly_report import make_nightly_report  # импорт внутри, чтобы не тянуть лишнее

    tz = timezone(timedelta(hours=TZ_OFFSET_HOURS))
    while True:
        now = datetime.now(tz=tz)
        run_at = _next_run(now)
        sleep_s = (run_at - now).total_seconds()
        log.info("Nightly report scheduled for %s (in %.0f s)", run_at.isoformat(), sleep_s)
        await asyncio.sleep(sleep_s)

        try:
            text = await make_nightly_report()
            if CHANNEL_ID != 0:
                await bot.send_message(CHANNEL_ID, text, disable_web_page_preview=True)
                log.info("Nightly report sent to %s", CHANNEL_ID)
            else:
                log.warning("HQ_CHANNEL_ID is not set; skipping send.")
        except Exception as e:
            log.exception("Nightly report failed: %s", e)
            # Спим минуту и продолжаем цикл
            await asyncio.sleep(60)


async def main() -> None:
    # здесь МОЖНО добавлять дополнительные периодические задачи
    await nightly_loop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        # закрыть http-сессию бота корректно
        try:
            asyncio.run(bot.session.close())
        except RuntimeError:
            pass
