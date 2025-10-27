import asyncio
import logging
import os
import signal
import sys
from datetime import datetime, timezone, timedelta
from typing import Optional

from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

# ==========
# ENV & LOGS
# ==========
TZ = os.getenv("TZ_DEFAULT", "Europe/Moscow")
# для логов: DEBUG/INFO/WARNING
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
log = logging.getLogger("main")

BOT_TOKEN = os.environ["BOT_TOKEN"]  # обязательно
MODE = os.getenv("MODE", os.getenv("ENV", "polling")).lower()  # polling | webhook
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # если используете вебхуки
PORT = int(os.getenv("PORT", "8000"))   # для webhook
BUILD = os.getenv("BUILD_MARK", os.getenv("BUILD", "unknown"))
SHA = os.getenv("BUILD_SHA", os.getenv("SHA", "manual"))
ENV_NAME = os.getenv("ENV", "polling")

# Uptime
STARTED_AT = datetime.now(timezone.utc)

# ======
# ROUTER
# ======
router = Router()


def _fmt_uptime() -> str:
    delta: timedelta = datetime.now(timezone.utc) - STARTED_AT
    secs = int(delta.total_seconds())
    h, r = divmod(secs, 3600)
    m, s = divmod(r, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


@router.message(CommandStart())
async def cmd_start(m: Message):
    text = (
        "Привет! Я на связи.\n"
        "Доступные команды:\n"
        "/status — технический статус\n"
        "/diag — диагностический пинг\n"
        "/hq — сводка\n"
        "/help — справка"
    )
    await m.answer(text)


@router.message(Command("help"))
async def cmd_help(m: Message):
    await m.answer("Команды: /start /status /diag /hq /ping")


@router.message(Command("ping") | Command("diag"))
async def cmd_ping(m: Message):
    await m.answer("pong ✅")


@router.message(Command("status"))
async def cmd_status(m: Message):
    await m.answer("OK ✅")


@router.message(Command("hq"))
async def cmd_hq(m: Message):
    text = (
        "🏷️ HQ-сводка\n"
        f"• ENV: <b>{ENV_NAME}</b>  • MODE: <b>{MODE}</b>\n"
        f"• BUILD: <code>{BUILD}</code>  • SHA: <code>{SHA}</code>\n"
        f"• Uptime: <code>{_fmt_uptime()}</code>\n"
        "• Отчёты: не найден (проверьте daily/post-deploy отчёты)"
    )
    await m.answer(text, parse_mode="HTML")


# =========================
# LIFECYCLE & APP STARTUP
# =========================
bot: Optional[Bot] = None
dp: Optional[Dispatcher] = None
_shutdown_event = asyncio.Event()


async def on_startup():
    # тут можно подгрузить ваши под-роутеры (casting/apply/faq/hq/ping и т.п.)
    log.info("Startup hook done.")


async def on_shutdown():
    log.info("Shutdown hook: closing bot session...")
    if bot:
        await bot.session.close()
    log.info("Shutdown completed.")


def _install_signals(loop: asyncio.AbstractEventLoop):
    # корректная остановка по SIGTERM/SIGINT (Render шлёт SIGTERM на рестарт)
    def _handler(sig, frame):
        log.warning("Received %s — shutting down gracefully...", sig.name)
        _shutdown_event.set()

    for s in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(s, _handler, s, None)
        except NotImplementedError:
            # Windows / PyCharm fallback
            signal.signal(s, _handler)


async def run_polling():
    global bot, dp
    bot = Bot(BOT_TOKEN, parse_mode="HTML")
    dp = Dispatcher()
    dp.include_router(router)

    await on_startup()

    # На всякий случай удалим webhook (если раньше был включен)
    try:
        await bot.delete_webhook(drop_pending_updates=False)
    except Exception as e:
        log.warning("delete_webhook warning: %s", e)

    # Стартуем polling
    log.info("aiogram.dispatcher: Start polling..")
    polling = asyncio.create_task(dp.start_polling(bot, allowed_updates=None))

    # ждём сигнала на остановку
    await _shutdown_event.wait()
    polling.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await polling

    await on_shutdown()


async def run_webhook():
    """
    Вебхуки имеют смысл только если у вас есть внешний входящий HTTP (например, Render Web Service).
    Для worker лучше использовать polling.
    """
    from aiohttp import web
    from aiogram.webhook.aiohttp_server import (
        SimpleRequestHandler,
        setup_application,
    )

    if not WEBHOOK_URL:
        raise RuntimeError("WEBHOOK_URL is not set")

    global bot, dp
    bot = Bot(BOT_TOKEN, parse_mode="HTML")
    dp = Dispatcher()
    dp.include_router(router)

    await on_startup()

    app = web.Application()
    webhook_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    webhook_handler.register(app, path="/webhook")

    setup_application(app, dp, bot=bot)

    # Устанавливаем webhook
    await bot.set_webhook(url=f"{WEBHOOK_URL}/webhook", drop_pending_updates=True)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    log.info("Webhook up on 0.0.0.0:%s", PORT)

    await _shutdown_event.wait()

    await runner.cleanup()
    await on_shutdown()


# =========
# MAIN
# =========
import contextlib

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    _install_signals(loop)

    try:
        if MODE == "webhook":
            loop.run_until_complete(run_webhook())
        else:
            # по умолчанию — polling (надёжнее на Render Worker)
            loop.run_until_complete(run_polling())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        log.exception("Fatal error: %s", e)
        sys.exit(1)
    finally:
        # safety
        if bot:
            loop.run_until_complete(bot.session.close())
        loop.close()
