# app/routers/diag.py
from __future__ import annotations

import os
from datetime import datetime, timezone
from fastapi import APIRouter, Request, HTTPException
from aiogram import Router, types
from aiogram.filters import Command

# --- FastAPI router (web mode) ---
web_router = APIRouter()

STATUS_KEY = os.getenv("STATUS_KEY", "")


def _bool_env(name: str, default: bool = True) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.lower() not in {"0", "false", "no"}


@web_router.get("/status_json")
async def status_json(request: Request, key: str | None = None):
    if STATUS_KEY and key != STATUS_KEY:
        raise HTTPException(status_code=403, detail="forbidden")

    data = {
        "env": os.getenv("ENV", "develop"),
        "build_mark": os.getenv("BUILD_MARK", "deploy-unknown"),
        "git_sha": os.getenv("GIT_SHA", "")[:7],
        "image": os.getenv("IMAGE", "ghcr.io/<owner>/<repo>:develop"),
        "render_status": "live",
        "sentry_ok": _bool_env("SENTRY_OK", True),
        "cronitor_ok": _bool_env("CRONITOR_OK", True),
        "cronitor_last_ping_iso": os.getenv("CRONITOR_LAST_PING_ISO", ""),
        "bot_time_iso": datetime.now(timezone.utc).isoformat(),
        "uptime_sec": int(float(os.getenv("UPTIME_SEC", "0"))),
    }
    return data


# --- Aiogram router (worker mode) ---
bot_router = Router(name="diag")


@bot_router.message(Command("ping"))
async def cmd_ping(message: types.Message):
    await message.answer("pong 🟢")


@bot_router.message(Command("who"))
async def cmd_who(message: types.Message):
    user = message.from_user
    await message.answer(f"id={user.id}, name={user.full_name}")


# --- export selection (so main.py can use the right one) ---
def get_router(mode: str):
    """Выбирает подходящий router по режиму запуска"""
    if mode == "web":
        return web_router
    return bot_router


__all__ = ["get_router", "web_router", "bot_router"]
