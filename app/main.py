from __future__ import annotations
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

# FastAPI-приложение (ВАЖНО: объект называется app)
app = FastAPI(title="Elaya StageCoach", version=BUILD_MARK)

@app.get("/healthz")
async def healthz():
    # Простой healthcheck для Render
    loop = asyncio.get_event_loop()
    return {"ok": True, "uptime_s": int(loop.time())}

async def start_polling() -> None:
    global dp, bot
    bot = Bot(
        token=settings.TG_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    try:
        # Снимаем вебхук, чтобы не конфликтовал с getUpdates
        try:
            await bot.delete_webhook(drop_pending_updates=True)
            logger.info("Webhook deleted (drop_pending_updates=True).")
        except TelegramBadRequest as e:
            logger.warning("delete_webhook: %s (ignored)", e)

        dp = Dispatcher()

        # Роутеры подключаем только тут, чтобы web-процесс их не тянул
        from app.routers import (
            entrypoints,
            help as help_router,
            cmd_aliases,
            onboarding,
            system,
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
            hq,
        )
        dp.include_router(entrypoints.router)
        dp.include_router(help_router.router)
        dp.include_router(cmd_aliases.router)
        dp.include_router(onboarding.router)
        dp.include_router(system.router)
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
        dp.include_router(hq.router)

        logger.info(
            "bot router loaded; ENV=%s MODE=%s BUILD=%s",
            settings.ENV, settings.MODE, BUILD_MARK,
        )
        await dp.start_polling(bot)

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
    Точка входа при запуске как модуля.
    MODE=web    -> вернём FastAPI app (uvicorn стартует из entrypoint.py)
    MODE=worker -> запустим aiogram polling
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
