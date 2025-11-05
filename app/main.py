# app/main.py
from __future__ import annotations

import asyncio
import logging
import os
from typing import Optional

from fastapi import FastAPI, Request, Response, status
from fastapi.responses import PlainTextResponse, JSONResponse

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Update

# опциональные импорты — не обязательны для запуска
try:
    from app.build import BUILD_MARK  # метка сборки, если есть
except Exception:  # pragma: no cover
    BUILD_MARK = "dev"

try:
    # инициализация схемы БД, если есть реализация
    from app.storage.repo import ensure_schema  # type: ignore
except Exception:  # pragma: no cover
    async def ensure_schema() -> None:
        return None


# --------------------------
# Логирование
# --------------------------
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
log = logging.getLogger("elaya.main")


# --------------------------
# Конфиг из окружения
# --------------------------
BOT_PROFILE: str = os.getenv("BOT_PROFILE", "hq").strip()
TELEGRAM_TOKEN: Optional[str] = os.getenv("TELEGRAM_TOKEN")
BASE_URL: Optional[str] = os.getenv("STAGECOACH_WEB_URL")  # напр., https://elaya-trainer-bot.onrender.com
WEBHOOK_PATH = "/tg/webhook"
WEBHOOK_URL: Optional[str] = f"{BASE_URL}{WEBHOOK_PATH}" if BASE_URL else None


# --------------------------
# Глобальные объекты
# --------------------------
app = FastAPI(title="Elaya StageCoach", version="1.0")

bot: Optional[Bot] = None
dp: Optional[Dispatcher] = None


# --------------------------
# Подключение роутеров по профилю
# --------------------------
def _safe_include(module_path: str) -> None:
    """Безопасно заимпортировать модуль и включить его router, если он есть."""
    global dp
    if dp is None:
        return
    try:
        module = __import__(module_path, fromlist=["router"])
        router = getattr(module, "router", None)
        if router:
            dp.include_router(router)
            log.info("Router loaded: %s", module_path)
        else:
            log.warning("No `router` in %s — skipped.", module_path)
    except Exception as e:
        log.warning("Cannot import %s: %s", module_path, e)


def include_profile_routers(profile: str) -> None:
    """
    Для hq: системные и штабные.
    Для trainer: пользовательские (меню/тренировки/прогресс) + системные.
    """
    if dp is None:
        return

    # всегда полезно иметь базовый system
    _safe_include("app.routers.system")

    if profile == "hq":
        _safe_include("app.routers.hq")
        _safe_include("app.routers.debug")
    else:  # trainer (или любой иной — трактуем как внешний контур)
        _safe_include("app.routers.menu")
        _safe_include("app.routers.training")
        _safe_include("app.routers.progress")
        # отладочный быстрый пинг (если есть)
        _safe_include("app.routers.debug")


# --------------------------
# Жизненный цикл
# --------------------------
@app.on_event("startup")
async def on_startup() -> None:
    global bot, dp

    # инициализируем БД, если есть
    await ensure_schema()

    if not TELEGRAM_TOKEN:
        log.error("Env TELEGRAM_TOKEN is not set — bot disabled, web will work.")
        return

    bot = Bot(
        token=TELEGRAM_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    # роутеры под профиль
    include_profile_routers(BOT_PROFILE)

    # вебхук
    if WEBHOOK_URL:
        try:
            await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True, allowed_updates=["message"])
            me = await bot.get_me()
            log.info("Webhook set for @%s → %s", me.username, WEBHOOK_URL)
        except Exception as e:  # pragma: no cover
            log.exception("Failed to set webhook: %s", e)
    else:
        log.warning("STAGECOACH_WEB_URL is not set — webhook URL cannot be computed.")

    log.info("Startup complete | profile=%s | build=%s", BOT_PROFILE, BUILD_MARK)


@app.on_event("shutdown")
async def on_shutdown() -> None:
    if bot:
        try:
            await bot.delete_webhook(drop_pending_updates=False)
        except Exception:
            pass
        await bot.session.close()
    log.info("Shutdown complete.")


# --------------------------
# HTTP эндпоинты
# --------------------------
@app.get("/", response_class=PlainTextResponse)
async def root() -> str:
    return "Elaya StageCoach web is alive."


@app.get("/healthz", response_class=PlainTextResponse)
async def healthz() -> str:
    return "ok"


@app.get("/build")
async def build() -> JSONResponse:
    return JSONResponse({"build": BUILD_MARK, "profile": BOT_PROFILE})


@app.post(WEBHOOK_PATH)
async def tg_webhook(request: Request) -> Response:
    """
    Общая точка входа вебхука Telegram.
    """
    global bot, dp

    if bot is None or dp is None:
        # бот не инициализирован (нет токена)
        return Response(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)

    data = await request.json()
    try:
        update = Update.model_validate(data)
        await dp.feed_update(bot, update)
    except Exception as e:
        log.exception("Failed to process update: %s | payload=%s", e, data)
        # Telegram ожидает 200/204, иначе будет ретрайть.
    return Response(status_code=status.HTTP_200_OK)


# --------------------------
# Локальный запуск (опционально)
# --------------------------
if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    # локально удобно дергать http://localhost:8000/healthz
    uvicorn.run("app.main:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")), reload=False)
