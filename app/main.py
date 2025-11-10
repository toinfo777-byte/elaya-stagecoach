from __future__ import annotations

import logging
import os
from typing import Any

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Update
from fastapi import FastAPI, Request, Response, status
from starlette.responses import PlainTextResponse

from app.build import BUILD_MARK
from app.config import settings
from app.core import store  # init DB + антидубли

# --- FastAPI core -----------------------------------------------------------
app = FastAPI(title="Elaya StageCoach", version=BUILD_MARK)
dp = Dispatcher()

BOT_PROFILE = os.getenv("BOT_PROFILE", "hq").strip().lower()
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "").strip()

# --- aiogram-роутеры --------------------------------------------------------
from app.routers import system, hq  # базовые штабные
dp.include_router(system.router)
dp.include_router(hq.router)

if BOT_PROFILE == "trainer":
    # фронтовой контур «Тренер сцены»
    from app.routers import trainer
    dp.include_router(trainer.router)

# --- fastapi-роутеры --------------------------------------------------------
from app import core_api as core_api_router
from app.routers import diag

app.include_router(diag.router)          # /diag/...
app.include_router(core_api_router.router)

# Sentry breadcrumbs (мягкая трассировка запросов)
try:
    from app.mw_sentry import SentryBreadcrumbs
    app.add_middleware(SentryBreadcrumbs)
except Exception:
    logging.getLogger(__name__).warning("Sentry middleware not attached")

# --- singletons -------------------------------------------------------------
_bot: Bot | None = None


def get_bot() -> Bot:
    global _bot
    if _bot is None:
        _bot = Bot(
            token=settings.TELEGRAM_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )
    return _bot


# --- health -----------------------------------------------------------------
@app.get("/healthz")
async def healthz() -> PlainTextResponse:
    return PlainTextResponse("OK", status_code=200)


# --- telegram webhook --------------------------------------------------------
@app.post("/tg/webhook")
async def tg_webhook(request: Request) -> Response:
    # (1) проверка секрета, если включён
    if WEBHOOK_SECRET:
        req_secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
        if req_secret != WEBHOOK_SECRET:
            return Response(status_code=status.HTTP_403_FORBIDDEN)

    # (2) валидация апдейта
    try:
        data: dict[str, Any] = await request.json()
        update = Update.model_validate(data)
    except Exception:
        return Response(status_code=status.HTTP_400_BAD_REQUEST)

    # (3) антидубли по update_id — подтверждаем дубль молча
    if getattr(update, "update_id", None) is not None:
        try:
            if store.is_duplicate_update(int(update.update_id)):
                return Response(status_code=status.HTTP_200_OK)
        except Exception:
            logging.exception("duplicate check failed")

    # (4) прокармливаем апдейт диспетчеру
    bot = get_bot()
    try:
        await dp.feed_update(bot, update)
    except Exception:
        logging.exception("dp.feed_update failed")
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(status_code=status.HTTP_200_OK)


# --- lifecycle ---------------------------------------------------------------
@app.on_event("startup")
async def on_startup() -> None:
    try:
        store.init_db()  # создаёт таблицы и индексы, если их нет
    except Exception:
        logging.exception("store.init_db failed")

    logging.getLogger(__name__).info(
        "Startup: profile=%s build=%s env=%s",
        BOT_PROFILE,
        BUILD_MARK,
        os.getenv("ENV", "unknown"),
    )


@app.on_event("shutdown")
async def on_shutdown() -> None:
    bot = _bot
    if bot:
        await bot.session.close()
