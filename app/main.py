# app/main.py
from __future__ import annotations

import asyncio
import logging
import signal
from contextlib import asynccontextmanager

from fastapi import FastAPI

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.config import settings

# --- опционально: ваши утилиты (не обязательны для запуска) ---
try:
    from app.storage.repo import ensure_schema  # если есть миграции/инициализация
except Exception:  # noqa: BLE001
    ensure_schema = None

try:
    from app.build import BUILD_MARK  # если в проекте есть сборочный маркер
except Exception:  # noqa: BLE001
    BUILD_MARK = "dev"

# --- Роутеры FastAPI (подключайте то, что реально есть в репозитории) ---
# Пример: from app.routers import entrypoints, health, hq, ...
# Ниже аккуратная попытка подключить, но без падения, если модулей нет.
def include_optional_routers(app_: FastAPI) -> None:
    try:
        from app.routers import entrypoints
        app_.include_router(entrypoints.router)
    except Exception:
        pass

    try:
        from app.routers import help as help_router
        app_.include_router(help_router.router)
    except Exception:
        pass

    # Добавьте здесь остальные ваши роутеры по аналогии:
    # try:
    #     from app.routers import hq, privacy, training, progress, ...
    #     app_.include_router(hq.router)
    #     ...
    # except Exception:
    #     pass


# ------------- Aiogram section -------------
dp: Dispatcher | None = None
bot: Bot | None = None


async def start_polling() -> None:
    """Стартуем polling только если MODE = polling/bot и есть токен."""
    global dp, bot

    token = settings.EFFECTIVE_BOT_TOKEN
    if not token:
        logging.warning("Polling skipped: no BOT_TOKEN/TG_BOT_TOKEN provided.")
        return

    # Создаём бота и диспетчер
    bot = Bot(token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    # Подключаем aiogram-роутеры, если они есть
    try:
        from app.routers import (
            entrypoints as tg_entrypoints,
            help as tg_help,
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
            # diag,  # добавьте при наличии
        )

        dp.include_router(tg_entrypoints.router)
        dp.include_router(tg_help.router)
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
        # dp.include_router(diag.router)
    except Exception:
        # Если aiogram-роутеров нет/переименованы — запускаем чистый dp
        logging.getLogger(__name__).warning("Aiogram routers not linked; running bare Dispatcher.")

    logging.info("🚀 Start polling… [mode=%s, build=%s]", settings.MODE, BUILD_MARK)
    await dp.start_polling(bot, allowed_updates=None)  # None = все типы


async def stop_polling() -> None:
    """Корректная остановка aiogram."""
    global dp, bot
    try:
        if dp:
            await dp.storage.close()
            await dp.fsm.storage.close()  # если используется FSMStorage
    except Exception:
        pass
    try:
        if bot:
            await bot.session.close()
    except Exception:
        pass
    dp = None
    bot = None


# ------------- FastAPI section -------------
@asynccontextmanager
async def lifespan(app_: FastAPI):
    # Инициализация БД/схем — если в проекте предусмотрено
    if ensure_schema is not None:
        try:
            await ensure_schema()
        except Exception:  # noqa: BLE001
            logging.getLogger(__name__).warning("ensure_schema() skipped or failed.", exc_info=True)

    # Если процесс не web — поднимем polling в фоне
    polling_task: asyncio.Task | None = None
    if settings.is_polling:
        polling_task = asyncio.create_task(start_polling())

    # Передаём управление FastAPI
    yield

    # При остановке сервиса аккуратно гасим polling
    if polling_task:
        # отправим сигнал остановки polling
        try:
            await stop_polling()
        finally:
            try:
                polling_task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await polling_task
            except Exception:
                pass


def create_app() -> FastAPI:
    app_ = FastAPI(
        title="Elaya StageCoach",
        version=str(BUILD_MARK),
        lifespan=lifespan,
    )

    @app_.get("/health")
    async def health():
        return {"status": "ok", "mode": settings.MODE, "build": BUILD_MARK}

    include_optional_routers(app_)
    return app_


app = create_app()

# Локальный запуск uvicorn (не нужен на Render, но полезен локально):
# uvicorn app.main:app --reload
