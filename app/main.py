from __future__ import annotations

import asyncio
import importlib
import logging
import os
import time
from typing import Any, Dict, Iterable

from fastapi import FastAPI
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

START_TS = time.time()


def _include_optional_routers(_app: FastAPI) -> None:
    """Подключаем веб-роутеры, если они есть в проекте."""
    router_modules = [
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
        # "app.routers.diag",

        # внутренняя сцена (если есть)
        "app.scene.intro",
        "app.scene.reflect",
        "app.scene.transition",
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
            log.warning("router skipped: %s (%s)", mod_name, e)


_include_optional_routers(app)


# ---------- служебные эндпоинты

@app.get("/healthz")
def healthz() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/status_json")
def status_json() -> JSONResponse:
    uptime_sec = int(time.time() - START_TS)
    h, rem = divmod(uptime_sec, 3600)
    m, _ = divmod(rem, 60)
    uptime_str = f"{h}h {m}m"

    payload = {
        "env": os.getenv("ENV", "staging"),
        "mode": os.getenv("MODE", "web"),
        "service": "web",
        "build": os.getenv("BUILD_SHA", "local"),
        "sha": os.getenv("RENDER_GIT_COMMIT", "manual"),
        "uptime": uptime_str,

        # HQ-поля
        "status_emoji": os.getenv("HQ_STATUS_EMOJI", "🌞"),
        "status_word": os.getenv("HQ_STATUS_WORD", "Stable"),
        "focus": os.getenv("HQ_STATUS_FOCUS", "Система в ритме дыхания"),
        "note": os.getenv("HQ_STATUS_NOTE", "Web и Bot синхронны; пульс ровный."),
        "quote": os.getenv("HQ_STATUS_QUOTE", "«Ноябрь — дыхание изнутри.»"),
    }
    return JSONResponse(payload)


# ---------- точка входа воркера (aiogram polling)

async def run_worker() -> None:
    """
    Aiogram-polling воркер: подключаем все роутеры,
    вешаем GroupCommandGate для групп.
    """
    from aiogram import Bot, Dispatcher
    from aiogram.client.default import DefaultBotProperties
    from aiogram.enums import ParseMode

    from app.middlewares.group_gate import GroupCommandGate

    token = os.getenv("TG_BOT_TOKEN") or os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("TG_BOT_TOKEN (или BOT_TOKEN) is not set")

    bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    # --- Жёсткая калитка для групп
    default_whitelist = {"/hq", "/healthz"}
    env_extra = {c.strip() for c in os.getenv("ALLOW_GROUP_COMMANDS", "").split(",") if c.strip()}
    allowed = default_whitelist | env_extra
    dp.message.middleware(GroupCommandGate(allowed))
    dp.callback_query.middleware(GroupCommandGate(allowed))

    # --- Роутеры бота
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
        # "app.routers.diag",

        "app.scene.intro",
        "app.scene.reflect",
        "app.scene.transition",
    ]
    for name in modules:
        try:
            mod = importlib.import_module(name)
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


# ---------- точка запуска

if __name__ == "__main__":
    mode = os.getenv("MODE", "web").lower()
    if mode in ("worker", "polling"):
        asyncio.run(run_worker())
    else:
        import uvicorn
        uvicorn.run(
            "app.main:app",
            host=os.getenv("HOST", "0.0.0.0"),
            port=int(os.getenv("PORT", "10000")),
            log_level=os.getenv("LOG_LEVEL", "info"),
        )
