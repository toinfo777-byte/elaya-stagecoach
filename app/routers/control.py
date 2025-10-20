# app/routers/control.py
from __future__ import annotations

import asyncio
import os
import sys

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.control.admin import AdminOnly, is_admin
from app.control.utils import uptime_str, env_or
from app.control.notifier import notify_admins
from app.control.github_sync import send_status_sync  # <-- для /sync

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


@router.message(Command("sync"), AdminOnly())
async def cmd_sync(message: Message) -> None:
    """
    Формат: первая строка — имя блока, затем пустая строка и markdown-контент.
    Можно прислать текст в caption или реплаем.

    Примеры:
      /sync Блок 3 — Управляемость

      *Markdown...*

    Или: отправляешь сообщение с markdown и делаешь reply командой /sync
    """
    # Текст может прийти в разных местах
    raw_cmd_tail = (message.text or "").split(None, 1)
    if len(raw_cmd_tail) == 1 and (message.caption or message.reply_to_message):
        raw = message.caption or (message.reply_to_message.text or "")
    else:
        raw = raw_cmd_tail[1] if len(raw_cmd_tail) > 1 else ""

    if not raw.strip():
        return await message.reply(
            "Формат:\n`/sync Блок N — Название\\n\\n<markdown>`\n"
            "Первая строка — имя блока, затем пустая строка и содержимое.",
            parse_mode="Markdown"
        )

    lines = raw.splitlines()
    block = lines[0].strip()
    content = "\n".join(
        lines[2:] if len(lines) > 1 and lines[1].strip() == "" else lines[1:]
    ).strip()

    if not block or not content:
        return await message.reply("Нужно указать имя блока и markdown-контент.")

    try:
        await send_status_sync(block, content)
    except Exception as e:
        return await message.reply(f"❌ Не получилось отправить в GitHub: {e}")

    await message.reply(
        f"✅ Отправлено в GitHub: `{block}`. Ждём workflow.",
        parse_mode="Markdown"
    )
