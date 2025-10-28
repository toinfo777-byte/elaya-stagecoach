from __future__ import annotations

import asyncio
import importlib
import logging
import os
import time
from typing import Any, Dict

from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse

# ---------- базовый логгер
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
log = logging.getLogger("elaya.main")

# ---------- FastAPI
app = FastAPI(
    title="Elaya Stagecoach — Web",
    version=os.getenv("BUILD_SHA", "local"),
)


# Подключаем твои роутеры, если есть (мягко — без падений, как только файл появится — подхватится)
def _include_optional_routers(_app: FastAPI) -> None:
    router_modules = [
        # добавляй/снимай по вкусу — порядок не критичен
        "app.routers.faq",
        "app.routers.devops_sync",
        "app.routers.hq",
        "app.routers.system",
        "app.routers.entrypoints",
        "app.routers.help",
        "app.routers.cmd_aliases",
        "app.routers.onboarding",
        "app.routers.leader",
        "app.routers.training",
        "app.routers.progress",
        "app.routers.privacy",
        "app.routers.settings",
        "app.routers.extended",
        "app.routers.casting",
        "app.routers.apply",
        # "app.routers.diag",  # если понадобится
    ]
    for mod_name in router_modules:
        try:
            mod = importlib.import_module(mod_name)
            router = getattr(mod, "router", None)
            if router is not None:
                _app.include_router(router)
                log.info("router loaded: %s", mod_name)
            else:
                log.debug("module has no router: %s", mod_name)
        except Exception as e:
            # Не валим web, просто логируем
            log.warning("router skipped: %s (%s)", mod_name, e)


_include_optional_routers(app)


# ---------- служебные эндпоинты

@app.get("/healthz")
def healthz() -> Dict[str, str]:
    # Лёгкий endpoint для Render Health Check
    return {"status": "ok"}


@app.get("/status_json")
def status_json() -> JSONResponse:
    # Быстрый отчёт, чтобы HQ-бот/панель могли дёргать состояние web
    payload = {
        "env": os.getenv("ENV", "staging"),
        "mode": os.getenv("MODE", "web"),
        "build": os.getenv("BUILD_SHA", "local"),
        "sha": os.getenv("RENDER_GIT_COMMIT", "manual"),
        "uptime": int(time.time() - START_TS),
        "service": "web",
    }
    return JSONResponse(payload)


# ---------- точка входа воркера (aiogram polling)

async def run_worker() -> None:
    from aiogram import Bot, Dispatcher
    from aiogram.client.default import DefaultBotProperties
    from aiogram.enums import ParseMode

    token = os.getenv("TG_BOT_TOKEN")
    if not token:
        raise RuntimeError("TG_BOT_TOKEN is not set")

    bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    # Пытаемся подключить те же роутеры, если они содержат aiogram-хендлеры
    modules = [
        "app.routers.faq",
        "app.routers.devops_sync",
        "app.routers.hq",
        "app.routers.system",
        "app.routers.entrypoints",
        "app.routers.help",
        "app.routers.cmd_aliases",
        "app.routers.onboarding",
        "app.routers.leader",
        "app.routers.training",
        "app.routers.progress",
        "app.routers.privacy",
        "app.routers.settings",
        "app.routers.extended",
        "app.routers.casting",
        "app.routers.apply",
    ]
    for name in modules:
        try:
            mod = importlib.import_module(name)
            # поддерживаем оба варианта: dp/routers или register(dp)
            if hasattr(mod, "router"):
                dp.include_router(getattr(mod, "router"))
                log.info("bot router loaded: %s", name)
            elif hasattr(mod, "register"):
                getattr(mod, "register")(dp)
                log.info("bot register called: %s", name)
        except Exception as e:
            log.warning("bot router skipped: %s (%s)", name, e)

    log.info("🧭 Start polling…")
    await dp.start_polling(bot)


# ---------- локальный запуск (Render вызывает через entrypoint.sh)

START_TS = time.time()

if __name__ == "__main__":
    mode = os.getenv("MODE", "web").lower()
    if mode in ("worker", "polling"):
        asyncio.run(run_worker())
    else:
        # Локально: uvicorn app.main:app --reload
        import uvicorn

        uvicorn.run(
            "app.main:app",
            host=os.getenv("HOST", "0.0.0.0"),
            port=int(os.getenv("PORT", "10000")),
            log_level=os.getenv("LOG_LEVEL", "info"),
        )
