# app/routers/control.py
from __future__ import annotations

import asyncio
import os
import sys
from typing import Optional

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.control.admin import AdminOnly
from app.control.utils import uptime_str, env_or
from app.control.notifier import notify_admins
from app.control.github_sync import send_status_sync  # для /sync

import aiohttp

router = Router(name="control")

BUILD = env_or("SHORT_SHA", "local")
ENV   = env_or("ENV", "develop")
IMAGE = env_or("IMAGE_TAG", "ghcr.io/unknown/elaya-stagecoach:develop")
MARK  = env_or("BUILD_MARK", "local")

RAW_HOST = "https://raw.githubusercontent.com"
REPO     = os.getenv("GITHUB_REPOSITORY", "toinfo777-byte/elaya-stagecoach")
BRANCH   = os.getenv("REPORT_BRANCH", "main")

async def fetch_raw(session: aiohttp.ClientSession, url: str) -> Optional[str]:
    try:
        async with session.get(url, timeout=10) as r:
            if r.status == 200:
                return await r.text()
    except Exception:
        return None
    return None

@router.message(Command("status"))
async def cmd_status(message: Message) -> None:
    sentry_state   = "on" if os.getenv("SENTRY_DSN") else "off"
    cronitor_state = "on" if os.getenv("CRONITOR_PING_URL") else "on"  # health-URL опц.
    text = (
        "🧭 <b>Status</b>\n"
        f"• ENV: <code>{ENV}</code>\n"
        f"• BUILD_MARK: <code>{MARK}</code>\n"
        f"• GIT_SHA: <code>{BUILD}</code>\n"
        f"• IMAGE: <code>{IMAGE}</code>\n"
        f"• Uptime: <code>{uptime_str()}</code>\n"
        f"• Sentry: <code>{sentry_state}</code>\n"
        f"• Cronitor/HC: <code>{cronitor_state}</code>\n"
    )
    await message.answer(text)

@router.message(Command("version"))
async def cmd_version(message: Message) -> None:
    await message.answer(f"🧱 <b>Build:</b> <code>{BUILD}</code>\n🌿 <b>ENV:</b> <code>{ENV}</code>")

@router.message(Command("reload"), AdminOnly())
async def cmd_reload(message: Message) -> None:
    await message.answer("🔁 Перезапуск… (Render автоматически поднимет инстанс)")
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
    raw_cmd_tail = (message.text or "").split(None, 1)
    if len(raw_cmd_tail) == 1 and (message.caption or message.reply_to_message):
        raw = message.caption or (message.reply_to_message.text or "")
    else:
        raw = raw_cmd_tail[1] if len(raw_cmd_tail) > 1 else ""

    if not raw.strip():
        return await message.reply(
            "Формат:\n`/sync Блок N — Название\\n\\n<markdown>`",
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

    await message.reply(f"✅ Отправлено в GitHub: `{block}`. Ждём workflow.", parse_mode="Markdown")

@router.message(Command("report"))
async def cmd_report(message: Message) -> None:
    # тянем сегодняшний отчёт из main: docs/elaya_status/Elaya_Status_YYYY_MM_DD.md
    today = asyncio.get_event_loop().time()  # just to keep loop; date via datetime
    from datetime import datetime
    date_str = datetime.utcnow().strftime("%Y_%m_%d")
    path = f"docs/elaya_status/Elaya_Status_{date_str}.md"
    url  = f"{RAW_HOST}/{REPO}/{BRANCH}/{path}"

    header = (
        "🧾 <b>Ежедневный отчёт</b>\n"
        f"• ENV: <code>{ENV}</code>\n"
        f"• BUILD: <code>{MARK}</code>\n"
        f"• SHA: <code>{BUILD}</code>\n"
        f"• IMAGE: <code>{IMAGE}</code>\n"
        f"• Uptime: <code>{uptime_str()}</code>\n"
        f"• File: <code>{path}</code>\n"
    )

    async with aiohttp.ClientSession() as s:
        content = await fetch_raw(s, url)

    if content:
        # отправляем markdown как файл (txt), чтобы не резал TG
        await message.answer(header)
        await message.answer_document(
            document=("Elaya_Status.md", content.encode("utf-8")),
            caption="Приложен текущий Markdown-отчёт."
        )
    else:
        await message.answer(header + "\nФайл не найден в репозитории — отправлена только сводка.")
