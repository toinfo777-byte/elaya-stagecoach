from __future__ import annotations

import hashlib
import logging
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram import Bot

from app.build import BUILD_MARK

router = Router(name="diag")
log = logging.getLogger("diag")


@router.message(Command("build"))
async def cmd_build(m: Message):
    await m.answer(f"BUILD: <b>{BUILD_MARK}</b>")


@router.message(Command("who"))
async def cmd_who(m: Message, bot: Bot):
    me = await bot.get_me()
    token_hash = hashlib.md5((await bot.get_token()).encode()).hexdigest()[:8]
    await m.answer(
        "🤖 <b>Bot</b>\n"
        f"id: <code>{me.id}</code>\n"
        f"username: @{me.username}\n"
        f"name: {me.full_name}\n"
        f"token-hash: <code>{token_hash}</code>"
    )


@router.message(Command("webhook"))
async def cmd_webhook(m: Message, bot: Bot):
    info = await bot.get_webhook_info()
    await m.answer(
        "<b>Webhook</b>\n"
        f"url: <code>{info.url or ''}</code>\n"
        f"has_custom_certificate: {info.has_custom_certificate}\n"
        f"pending_update_count: {info.pending_update_count}"
    )

# Никаких catch-all здесь нет.
