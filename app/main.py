from __future__ import annotations

import asyncio
import importlib
import logging
import os
from typing import List

from fastapi import FastAPI
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.config import settings

logger = logging.getLogger("main")
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")

# ------------ FastAPI ------------
app = FastAPI(title="Elaya StageCoach", version=os.getenv("BUILD_MARK", "manual"))

def include_routers(fastapi_app: FastAPI, modules: List[str]) -> None:
    """Динамическое подключение роутеров FastAPI, если они есть (можно оставить пустым)."""
    for module_name in modules:
        try:
            mod = importlib.import_module(module_name)
            router = getattr(mod, "router", None)
            if router:
                fastapi_app.include_router(router)
                logger.info("fastapi router loaded: %s", module_name)
        except Exception as e:
            logger.error("router failed: %s (%s)", module_name, e)

# если у тебя есть web-роутеры — пропиши их здесь
include_routers(app, [
    # "app.routers.health",  # пример
])

@app.get("/healthz")
async def healthz():
    return {"status": "ok", "mode": settings.MODE, "build": os.getenv("BUILD_MARK", "manual")}

# ------------ Telegram Bot (aiogram) ------------
bot = Bot(
    token=settings.BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode(settings.PARSE_MODE)),
)
dp = Dispatcher()

def include_bot_routers(dispatcher: Dispatcher, modules: List[str]) -> None:
    for module_name in modules:
        try:
            mod = importlib.import_module(module_name)
            router = getattr(mod, "router", None)
            if router:
                dispatcher.include_router(router)
                logger.info("bot router loaded: %s", module_name)
        except Exception as e:
            logger.error("bot router failed: %s (%s)", module_name, e)

# перечисли свои aiogram-роутеры
include_bot_routers(dp, [
    # "app.routers.entrypoints",
    # "app.routers.help",
    # "app.routers.faq",
    # "app.routers.devops_sync",
    # "app.routers.hq",
    # и т.д.
])

async def run_polling() -> None:
    logger.info("🚀 Start polling…")
    await dp.start_polling(bot)

# Внимание: процесс запускается из entrypoint.sh
# - для worker: python -m app.main → здесь пойдём в polling
# - для web: uvicorn app.main:app → uvicorn поднимет FastAPI и НЕ вызовет polling

if __name__ == "__main__":
    # Запускаем только в режиме worker (для совместимости, если кто-то вызовет напрямую)
    if settings.MODE == "worker":
        asyncio.run(run_polling())
    else:
        # В режиме web управление передаст uvicorn через entrypoint.sh
        import uvicorn
        uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)
