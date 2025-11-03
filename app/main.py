from __future__ import annotations

import os
import asyncio
import logging
from typing import Optional

from fastapi import FastAPI
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramConflictError, TelegramBadRequest

from app.config import settings
from app.build import BUILD_MARK

dp: Optional[Dispatcher] = None
bot: Optional[Bot] = None

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("elaya.main")

# --- FastAPI app (для WEB сервиса) ---
app = FastAPI(title="Elaya StageCoach", version=BUILD_MARK)

@app.get("/healthz")
async def healthz():
    loop = asyncio.get_event_loop()
    return {"ok": True, "uptime_s": int(loop.time())}


def _include_routers_for_profile(dp: Dispatcher, profile: str) -> None:
    """
    Загружаем только нужные роутеры под ролью сервиса.
    profile:
      - "hq"       -> минимальный набор для HQ worker
      - "trainer"  -> пользовательские разделы тренера
      - "web"      -> если когда-то захотим отдельно под web
      - по умолчанию — как "hq"
    """
    # Общие системные вещи
    from app.routers import system, hq  # HQ-команды/статусы всегда нужны

    # Временный дебаг (можно отключить после проверки)
    try:
        from app.routers import debug
        dp.include_router(debug.router)
    except Exception as e:
        logger.warning("debug router not loaded: %s", e)

    # Базовые HQ
    dp.include_router(system.router)
    dp.include_router(hq.router)

    profile = (profile or "hq").lower()

    if profile == "trainer":
        # Подключаем пользовательские разделы Тренера
        from app.routers import (
            help as help_router,
            cmd_aliases,
            onboarding,
            minicasting,
            leader,
            training,
            progress,
            privacy,
            settings as settings_mod,
            extended,
            casting,
            apply,
            faq,
            devops_sync,
            panic,
        )
        dp.include_router(help_router.router)
        dp.include_router(cmd_aliases.router)
        dp.include_router(onboarding.router)
        dp.include_router(minicasting.router)
        dp.include_router(leader.router)
        dp.include_router(training.router)
        dp.include_router(progress.router)
        dp.include_router(privacy.router)
        dp.include_router(settings_mod.router)
        dp.include_router(extended.router)
        dp.include_router(casting.router)
        dp.include_router(apply.router)
        dp.include_router(faq.router)
        dp.include_router(devops_sync.router)
        dp.include_router(panic.router)

    elif profile == "web":
        # для чистого веб-профиля сейчас ничего не добавляем (FastAPI сам обслуживает /healthz)
        pass

    else:
        # "hq" / unknown -> только HQ-набор (system + hq + debug)
        pass


# --- Telegram Bot worker ---
async def start_polling() -> None:
    global dp, bot
    bot = Bot(
        token=settings.TG_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    try:
        # снимаем вебхук (во избежание конфликта с getUpdates)
        try:
            await bot.delete_webhook(drop_pending_updates=True)
            logger.info("Webhook deleted (drop_pending_updates=True).")
        except TelegramBadRequest as e:
            logger.warning("delete_webhook: %s (ignored)", e)

        dp = Dispatcher()

        profile = os.getenv("BOT_PROFILE", "hq")
        logger.info("Launching with BOT_PROFILE=%s", profile)
        _include_routers_for_profile(dp, profile)

        logger.info(
            "bot routers loaded; ENV=%s MODE=%s BUILD=%s",
            settings.ENV, settings.MODE, BUILD_MARK,
        )

        used = dp.resolve_used_update_types()
        logger.info("allowed_updates=%s", used)
        await dp.start_polling(bot, allowed_updates=used)

    except TelegramConflictError as e:
        logger.error(
            "TelegramConflictError: %s. Вероятен параллельный процесс с тем же токеном.",
            e,
        )
        await asyncio.sleep(5)
        raise
    finally:
        if dp:
            await dp.storage.close()
        if bot:
            await bot.session.close()


def run_app():
    """
    MODE=web    -> запускаем только FastAPI
    MODE=worker -> запускаем Telegram polling
    """
    if settings.MODE.lower() == "web":
        logger.info("Starting WEB app... ENV=%s MODE=web BUILD=%s", settings.ENV, BUILD_MARK)
        return app
    elif settings.MODE.lower() == "worker":
        logger.info("Starting BOT polling... ENV=%s MODE=worker BUILD=%s", settings.ENV, BUILD_MARK)
        asyncio.run(start_polling())
    else:
        raise RuntimeError(f"Unknown MODE={settings.MODE!r}")


if __name__ == "__main__":
    run_app()
