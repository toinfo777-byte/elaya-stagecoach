# app/routers/diag.py
from __future__ import annotations

import os
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Request

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

# ───────────────────────── FastAPI (web) ─────────────────────────
# Если у тебя есть web-сервис (uvicorn), этот роутер можно
# подключить туда. Он даёт /status_json.
api_router = APIRouter()

STATUS_KEY = os.getenv("STATUS_KEY", "")


def _bool_env(name: str, default: bool = True) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.lower() not in {"0", "false", "no"}


@api_router.get("/status_json")
async def status_json(request: Request, key: str | None = None):
    # Опциональная «защита» ключом
    if STATUS_KEY and key != STATUS_KEY:
        raise HTTPException(status_code=403, detail="forbidden")

    # Параметры берём из ENV (или с дефолтами)
    data = {
        "env": os.getenv("ENV", "develop"),
        "build": os.getenv("BUILD_MARK", "deploy-unknown"),
        "sha": (os.getenv("GIT_SHA", "") or os.getenv("BUILD_SHA", ""))[:7],
        "image": os.getenv("IMAGE", "ghcr.io/<owner>/<repo>:develop"),
        "render_status": os.getenv("RENDER_STATUS", "live"),
        "sentry_ok": _bool_env("SENTRY_OK", True),
        "cronitor_ok": _bool_env("CRONITOR_OK", True),
        "cronitor_last_ping_iso": os.getenv("CRONITOR_LAST_PING_ISO", ""),
        "bot_time_iso": datetime.now(timezone.utc).isoformat(),
        "uptime_sec": int(os.getenv("UPTIME_SEC", "0")),
        "mode": os.getenv("MODE", "worker"),
        "bot_id": os.getenv("BOT_ID", ""),
    }
    return data


# ───────────────────── Aiogram (бот) ─────────────────────
# Этот роутер подключается в Dispatcher (dp.include_router).
bot_router = Router(name="diag")


def _env_short() -> dict[str, str]:
    return {
        "env": os.getenv("ENV", "develop"),
        "mode": os.getenv("MODE", "worker"),
        "build": os.getenv("BUILD_MARK", "unknown"),
        "sha": (os.getenv("GIT_SHA", "") or os.getenv("BUILD_SHA", ""))[:7],
        "uptime": os.getenv("UPTIME_SEC", "n/a"),
    }


@bot_router.message(Command(commands=["ping"]))
async def cmd_ping(message: Message) -> None:
    await message.answer("🏓 pong")


@bot_router.message(Command(commands=["who", "diag"]))
async def cmd_who(message: Message) -> None:
    info = _env_short()
    text = (
        "🔎 <b>Диагностика</b>\n"
        f"• ENV: <code>{info['env']}</code>\n"
        f"• MODE: <code>{info['mode']}</code>\n"
        f"• BUILD: <code>{info['build']}</code>\n"
        f"• SHA: <code>{info['sha'] or 'unknown'}</code>\n"
        f"• Uptime: <code>{info['uptime']}</code>"
    )
    await message.answer(text)


# На всякий случай — фабрика, если где-то ждут функцию.
def get_router() -> Router:
    return bot_router
