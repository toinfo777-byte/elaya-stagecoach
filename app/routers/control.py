# app/routers/control.py
from __future__ import annotations

import os
import time

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram import Bot

from app.control.notifier import notify_admins

router = Router(name="control")

BUILD = os.getenv("SHORT_SHA", "local").strip() or "local"
ENV = os.getenv("ENV", "develop").strip() or "develop"
START_TS = time.time()


def _uptime() -> str:
    s = int(time.time() - START_TS)
    d, s = divmod(s, 86400)
    h, s = divmod(s, 3600)
    m, s = divmod(s, 60)
    parts = []
    if d: parts.append(f"{d}d")
    if h: parts.append(f"{h}h")
    if m: parts.append(f"{m}m")
    parts.append(f"{s}s")
    return " ".join(parts)


@router.message(Command("version"))
async def cmd_version(m: Message):
    await m.answer(f"🧩 <b>Build</b>: <code>{BUILD}</code>\nENV: <b>{ENV}</b>")


@router.message(Command("status"))
async def cmd_status(m: Message):
    await m.answer(
        "🛠 <b>Status</b>\n"
        f"• Build: <code>{BUILD}</code>\n"
        f"• ENV: <b>{ENV}</b>\n"
        f"• Uptime: <code>{_uptime()}</code>"
    )


@router.message(Command("reload"))
async def cmd_reload(m: Message):
    await m.answer("♻️ Перезапуск… (процесс завершится, Render поднимет его заново)")
    # мягко не будем — просто выходим; Render перезапустит
    os._exit(0)


@router.message(Command("notify_admins"))
async def cmd_notify(m: Message, bot: Bot):
    # всё после пробела — текст уведомления
    text = (m.text or "").partition(" ")[2].strip() or "Manual admin notify"
    ok = await notify_admins(bot, f"📣 {text}")
    await m.answer("✅ Уведомление отправлено" if ok else "⚠️ ADMIN_ALERT_CHAT_ID не задан")
