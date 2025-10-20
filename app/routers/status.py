# app/routers/status.py
from __future__ import annotations
import os
import time
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from app.build import BUILD

router = Router(name="status")

_started_at = time.monotonic()

def _uptime() -> str:
    sec = int(time.monotonic() - _started_at)
    h, r = divmod(sec, 3600)
    m, s = divmod(r, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"

@router.message(Command("status"))
async def cmd_status(message: Message) -> None:
    sentry_state = "on" if os.getenv("SENTRY_DSN") else "off"
    cronitor_state = "on" if os.getenv("CRONITOR_PING_URL") or os.getenv("HEALTHCHECKS_URL") else "off"

    text = (
        "🧭 <b>Status</b>\n"
        f"• ENV: <code>{BUILD.env}</code>\n"
        f"• BUILD_MARK: <code>{BUILD.build_mark}</code>\n"
        f"• GIT_SHA: <code>{BUILD.git_sha[:12]}</code>\n"
        f"• IMAGE: <code>{BUILD.image_tag}</code>\n"
        f"• Uptime: <code>{_uptime()}</code>\n"
        f"• Sentry: <code>{sentry_state}</code>\n"
        f"• Cronitor/HC: <code>{cronitor_state}</code>\n"
    )
    await message.answer(text)
