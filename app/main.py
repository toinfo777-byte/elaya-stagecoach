from __future__ import annotations

import asyncio
import importlib
import logging
import os
from typing import Optional

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import BotCommand, Message

# --- Project settings / optional imports
try:
    from app.config import settings  # your Pydantic settings
except Exception:  # fail-safe if config not available
    class _Stub:
        MODE: str = os.getenv("MODE", "polling")
        ENV: str = os.getenv("ENV", "dev")

    settings = _Stub()  # type: ignore

try:
    from app.storage.repo import ensure_schema
except Exception:
    def ensure_schema() -> None:
        pass

try:
    from app.build import BUILD_MARK  # e.g. git sha / timestamp
except Exception:
    BUILD_MARK = os.getenv("BUILD_SHA", "manual")

# ------------------------------
# Logging
# ------------------------------
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s | %(levelname)s | %(name)s: %(message)s",
)
log = logging.getLogger("main")

# ------------------------------
# Token resolution (BOT_TOKEN / TG_BOT_TOKEN)
# ------------------------------
def resolve_token() -> Optional[str]:
    # be gentle with missing attributes on settings
    token = None
    for key in ("BOT_TOKEN", "TG_BOT_TOKEN"):
        token = token or getattr(settings, key, None)
        token = token or os.getenv(key)
    return token

# ------------------------------
# FastAPI (web mode)
# ------------------------------
app = FastAPI(title="Elaya StageCoach", version=str(BUILD_MARK))

@app.get("/ping")
async def ping():
    return JSONResponse({"ok": True, "pong": True, "build": str(BUILD_MARK)})

@app.get("/status")
async def status():
    mode = getattr(settings, "MODE", os.getenv("MODE", "polling"))
    env = getattr(settings, "ENV", os.getenv("ENV", "dev"))
    return JSONResponse({"ok": True, "mode": mode, "env": env, "build": str(BUILD_MARK)})

# ------------------------------
# Aiogram (polling mode)
# ------------------------------
dp = Dispatcher()
diag_router = Router(name="diag")

@diag_router.message(Command(commands=["ping", "diag"]))
async def cmd_ping(m: Message):
    await m.answer("✅ pong")

dp.include_router(diag_router)

def _try_include_project_routers() -> None:
    """
    Подключаем твои роутеры, если они есть.
    Ничего страшного, если каких-то модулей нет — просто идём дальше.
    """
    try:
        mod = importlib.import_module("app.routers")
    except Exception as e:
        log.info("routers package not found: %s", e)
        return

    # ожидаемые имена внутри app.routers (router-объекты или подмодули с .router)
    maybe_names = [
        "entrypoints", "help", "cmd_aliases", "onboarding", "system",
        "minicasting", "leader", "training", "progress", "privacy",
        "settings", "extended", "casting", "apply", "faq",
        "devops_sync", "panic", "hq", "diag",
    ]

    for name in maybe_names:
        try:
            sub = getattr(mod, name)
            # если это подмодуль — подтянем его .router
            if hasattr(sub, "router"):
                dp.include_router(getattr(sub, "router"))
            elif isinstance(sub, Router):
                dp.include_router(sub)  # непосредственно Router
        except Exception as e:
            log.debug("skip router %s: %s", name, e)

_try_include_project_routers()

async def _set_bot_commands(bot: Bot) -> None:
    commands = [
        BotCommand(command="menu", description="Главное меню"),
        BotCommand(command="help", description="Помощь"),
        BotCommand(command="ping", description="Проверка ответа"),
    ]
    try:
        await bot.set_my_commands(commands)
    except Exception as e:
        log.warning("set_my_commands failed: %s", e)

async def run_polling() -> None:
    token = resolve_token()
    if not token:
        log.error("No BOT token found. Set BOT_TOKEN or TG_BOT_TOKEN env/setting.")
        # Для веб-сервиса это нормально; для worker — причина завершить.
        raise SystemExit(1)

    # инициализация схемы/БД, если есть
    try:
        ensure_schema()
    except Exception as e:
        log.warning("ensure_schema() failed: %s", e)

    bot = Bot(token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await _set_bot_commands(bot)

    log.info("🚀 Start polling… (build=%s)", BUILD_MARK)
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

# ------------------------------
# Entrypoint switch
# ------------------------------
def is_web_mode() -> bool:
    mode = str(getattr(settings, "MODE", os.getenv("MODE", "polling"))).lower()
    return mode in {"web", "api", "asgi", "uvicorn"}

def is_polling_mode() -> bool:
    mode = str(getattr(settings, "MODE", os.getenv("MODE", "polling"))).lower()
    return mode in {"polling", "bot", "worker"}

if __name__ == "__main__":
    # Локальный запуск: выбираем режим из MODE
    if is_polling_mode():
        asyncio.run(run_polling())
    else:
        # В контейнере web обычно запускает uvicorn: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
