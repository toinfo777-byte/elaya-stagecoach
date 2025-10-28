import asyncio
import logging
import os
import signal
import sys
from datetime import datetime, timezone

from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

# ---------- базовая настройка ----------

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    stream=sys.stdout,
)
log = logging.getLogger("app")

BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    log.error("ENV BOT_TOKEN is not set")
    sys.exit(1)

ENV = os.getenv("ENV", "staging")
MODE = os.getenv("MODE", "polling")
BUILD_MARK = os.getenv("BUILD_MARK", "manual")
TZ_DEFAULT = os.getenv("TZ_DEFAULT", "Europe/Moscow")

STARTED_AT = datetime.now(timezone.utc)

# ---------- aiogram v3 ----------

bot = Bot(BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher()
router = Router()
dp.include_router(router)


# ---------- helpers ----------

def uptime_human() -> str:
    delta = datetime.now(timezone.utc) - STARTED_AT
    secs = int(delta.total_seconds())
    d, r = divmod(secs, 86400)
    h, r = divmod(r, 3600)
    m, s = divmod(r, 60)
    parts = []
    if d: parts.append(f"{d}d")
    if d or h: parts.append(f"{h}h")
    if d or h or m: parts.append(f"{m}m")
    parts.append(f"{s}s")
    return " ".join(parts)


async def hq_text() -> str:
    me = await bot.get_me()
    return (
        "<b>HQ-сводка</b>\n"
        f"• ENV: <code>{ENV}</code>\n"
        f"• MODE: <code>{MODE}</code>\n"
        f"• BUILD: <code>{BUILD_MARK}</code>\n"
        f"• TZ: <code>{TZ_DEFAULT}</code>\n"
        f"• Bot: <code>@{me.username}</code> (id={me.id})\n"
        f"• Uptime: <code>{uptime_human()}</code>\n"
        "• Note: polling с авто-сбросом webhook\n"
    )


# ---------- handlers ----------

@router.message(CommandStart())
async def on_start(message: Message):
    await message.answer(
        "Команды и разделы: выбери нужное 🧭\n"
        "🏋️ Тренировка дня — ежедневная рутина 5–15 мин.\n"
        "📈 Мой прогресс — стрик и эпизоды за 7 дней.\n"
        "🎯 Мини-кастинг · 💥 Путь лидера\n"
        "🆘 Помощь / FAQ · ⚙️ Настройки\n"
        "📜 Политика · ⭐️ Расширенная версия"
    )


@router.message(Command(commands=["hq"]))
async def on_hq(message: Message):
    await message.answer(await hq_text())


@router.message(Command(commands=["ping", "diag"]))
async def on_ping(message: Message):
    me = await bot.get_me()
    await message.answer(
        f"pong · ok · @{me.username}\n"
        f"uptime: <code>{uptime_human()}</code>"
    )


# резервный “эхо”-ответ только в dev/staging
@router.message(F.text)
async def fallback(message: Message):
    if ENV != "prod":
        await message.answer("Команда не распознана. Попробуй /hq или /ping.")
    # в проде — молчим


# ---------- lifecycle ----------

stop_event = asyncio.Event()

def _graceful_shutdown(*_):
    log.warning("SIGTERM/SIGINT received — shutting down…")
    stop_event.set()

async def main():
    # ВАЖНО: перед polling всегда сбрасываем webhook,
    # чтобы избежать конфликтов “getUpdates / webhook”.
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        log.info("Webhook deleted (drop_pending_updates=True)")
    except Exception as e:
        log.warning("delete_webhook failed: %s", e)

    # Запускаем polling
    log.info("Starting polling…")
    polling = asyncio.create_task(dp.start_polling(bot, allowed_updates=None))

    # Ждём сигнала остановки
    await stop_event.wait()

    # Останавливаем polling корректно
    polling.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await polling

if __name__ == "__main__":
    import contextlib

    loop = asyncio.get_event_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, _graceful_shutdown)

    try:
        loop.run_until_complete(main())
    finally:
        loop.run_until_complete(bot.session.close())
        loop.close()
