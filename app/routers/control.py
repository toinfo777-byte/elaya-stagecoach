# app/routers/control.py
from __future__ import annotations

import asyncio
import os
import sys
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from app.control.admin import AdminOnly, is_admin
from app.control.utils import uptime_str, env_or
from app.control.notifier import notify_admins

router = Router(name="control")

BUILD = env_or("SHORT_SHA", "local")
ENV = env_or("ENV", "develop")

# ---- Public commands --------------------------------------------------------

@router.message(Command("status"))
async def cmd_status(message: Message) -> None:
    sentry_state = "on" if os.getenv("SENTRY_DSN") else "off"
    cronitor_state = "on" if os.getenv("CRONITOR_PING_URL") else "off"

    text = (
        "🧭 <b>Status</b>\n"
        f"• Build: <code>{BUILD}</code>\n"
        f"• ENV: <code>{ENV}</code>\n"
        f"• Uptime: <code>{uptime_str()}</code>\n"
        f"• Sentry: <code>{sentry_state}</code>\n"
        f"• Cronitor: <code>{cronitor_state}</code>\n"
    )
    await message.answer(text)

@router.message(Command("version"))
async def cmd_version(message: Message) -> None:
    await message.answer(f"🧱 <b>Build:</b> <code>{BUILD}</code>\n🌿 <b>ENV:</b> <code>{ENV}</code>")

# ---- Admin-only commands ----------------------------------------------------

@router.message(Command("reload"), AdminOnly())
async def cmd_reload(message: Message) -> None:
    await message.answer("🔁 Перезапуск… (Render автоматически поднимет инстанс)")
    # маленькая задержка, чтобы ответ успел уйти
    async def _bye() -> None:
        await asyncio.sleep(0.5)
        sys.exit(0)
    asyncio.create_task(_bye())

@router.message(Command("notify_admins"), AdminOnly())
async def cmd_notify_admins(message: Message) -> None:
    payload = message.text.split(maxsplit=1)
    txt = payload[1] if len(payload) > 1 else "(без текста)"
    prefix = f"🚨 [{ENV}] [{BUILD}]"
    count = await notify_admins(message.bot, f"{prefix} {txt}")
    await message.answer(f"✅ Ушло: {count} (TG) + зеркала (Sentry/Cronitor)")
