from __future__ import annotations

import asyncio
import os
import sys
import time

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.control.admin import AdminOnly
from app.control.notifier import notify_admins
from app.control.github_sync import send_status_sync
from app.build import BUILD

router = Router(name="control")

BUILD_SHA = BUILD.git_sha
BUILD_MARK = BUILD.build_mark
IMAGE_TAG = BUILD.image_tag
ENV = BUILD.env

_started_at = time.monotonic()
def _uptime_local() -> str:
    sec = int(time.monotonic() - _started_at)
    h, r = divmod(sec, 3600)
    m, s = divmod(r, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"

@router.message(Command("status"))
async def cmd_status(message: Message) -> None:
    sentry_state = "on" if os.getenv("SENTRY_DSN") else "off"
    cronitor_state = "on" if (os.getenv("CRONITOR_PING_URL") or os.getenv("HEALTHCHECKS_URL")) else "off"
    text = (
        "🧭 <b>Status</b>\n"
        f"• ENV: <code>{ENV}</code>\n"
        f"• BUILD_MARK: <code>{BUILD_MARK}</code>\n"
        f"• GIT_SHA: <code>{BUILD_SHA[:12]}</code>\n"
        f"• IMAGE: <code>{IMAGE_TAG}</code>\n"
        f"• Uptime: <code>{_uptime_local()}</code>\n"
        f"• Sentry: <code>{sentry_state}</code>\n"
        f"• Cronitor/HC: <code>{cronitor_state}</code>\n"
    )
    await message.answer(text)

@router.message(Command("version"))
async def cmd_version(message: Message) -> None:
    await message.answer(
        f"🧱 <b>Build:</b> <code>{BUILD_MARK}</code>\n"
        f"🔹 <b>SHA:</b> <code>{BUILD_SHA[:12]}</code>\n"
        f"🌿 <b>ENV:</b> <code>{ENV}</code>"
    )

@router.message(Command("diag"), AdminOnly())
async def cmd_diag(message: Message) -> None:
    """Быстрый отчёт о живости сервисов + тест-ивент Sentry и пинг Cronitor/HC один раз."""
    # Sentry probe
    if os.getenv("SENTRY_DSN"):
        try:
            import sentry_sdk
            sentry_sdk.capture_message("Elaya /diag probe")
            s = "sent"
        except Exception as e:
            s = f"fail ({e})"
    else:
        s = "off"

    # Cronitor/HC single ping
    url = (os.getenv("CRONITOR_PING_URL") or os.getenv("HEALTHCHECKS_URL") or "").strip()
    if url:
        import aiohttp, asyncio
        try:
            async with aiohttp.ClientSession() as sess:
                async with sess.get(url, timeout=10) as r:
                    await r.text()
            c = "ok"
        except Exception as e:
            c = f"fail ({e})"
    else:
        c = "off"

    text = (
        "🧪 <b>Diag</b>\n"
        f"• ENV: <code>{ENV}</code>  • BUILD: <code>{BUILD_MARK}</code>  • SHA: <code>{BUILD_SHA[:12]}</code>\n"
        f"• Sentry probe: <code>{s}</code>\n"
        f"• Cronitor/HC ping: <code>{c}</code>\n"
    )
    await message.answer(text)

@router.message(Command("reload"), AdminOnly())
async def cmd_reload(message: Message) -> None:
    await message.answer("🔁 Перезапуск… (Render автоматически поднимет инстанс)")
    async def _bye() -> None:
        await asyncio.sleep(0.5)
        sys.exit(0)
    asyncio.create_task(_bye())

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
