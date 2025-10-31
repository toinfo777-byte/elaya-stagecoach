from __future__ import annotations
import asyncio
import logging
import os
from typing import Optional

from fastapi import FastAPI
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramConflictError, TelegramBadRequest

# важное: импортируем настройки ОДИН раз
from app.config import settings
from app.build import BUILD_MARK

# Роутеры подключаем ТОЛЬКО в режиме worker
# чтобы web- приложение не тащило aiogram и не стартовало поллинг случайно.
dp: Optional[Dispatcher] = None
bot: Optional[Bot] = None

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("elaya.main")

app = FastAPI(title="Elaya StageCoach", version=BUILD_MARK)


@app.get("/healthz")
async def healthz():
    # лёгкий health для Render
    return {"ok": True, "uptime_s": int(asyncio.get_event_loop().time())}


async def start_polling() -> None:
    global dp, bot
    # Явно гасим вебхук, чтобы не было конфликта webhook vs getUpdates
    bot = Bot(
        token=settings.TG_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    try:
        try:
            await bot.delete_webhook(drop_pending_updates=True)
            logger.info("Webhook deleted (drop_pending_updates=True).")
        except TelegramBadRequest as e:
            # если вебхука не было — это ок
            logger.warning("delete_webhook: %s", e)

        dp = Dispatcher()

        # РОУТЕРЫ ПОДКЛЮЧАЕМ ЗДЕСЬ, чтобы web не импортировал их
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
            hq,  # HQ-репорт/статус
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
        dp.include_router(hq.router)  # команды /hq, /status, /healthz (бота)

        logger.info(
            "bot router loaded; ENV=%s MODE=%s BUILD=%s",
            settings.ENV,
            settings.MODE,
            BUILD_MARK,
        )

        await dp.start_polling(bot)

    except TelegramConflictError as e:
        logger.error(
            "TelegramConflictError: %s. "
            "Скорее всего, запущен второй процесс с тем же токеном.",
            e,
        )
        # Спим чуть-чуть, чтобы Render не устроил быструю перезапуск-карусель
        await asyncio.sleep(5)
        raise
    finally:
        if dp:
            await dp.storage.close()
        if bot:
            await bot.session.close()


def run_app():
    """
    Точка входа для Render.

    MODE=web    -> поднимаем только FastAPI (никаких импортов aiogram-роутеров)
    MODE=worker -> запускаем aiogram-поллинг с предварительным delete_webhook
    """
    if settings.MODE.lower() == "web":
        # Render сам вызовет uvicorn согласно Dockerfile/CMD.
        logger.info("Starting WEB app... ENV=%s MODE=web BUILD=%s", settings.ENV, BUILD_MARK)
        return app  # для uvicorn:app
    elif settings.MODE.lower() == "worker":
        logger.info("Starting BOT polling... ENV=%s MODE=worker BUILD=%s", settings.ENV, BUILD_MARK)
        asyncio.run(start_polling())
    else:
        raise RuntimeError(f"Unknown MODE={settings.MODE!r}")


# Если процесс запускается через `python -m app.main` — стартуем согласно MODE
if __name__ == "__main__":
    run_app()
