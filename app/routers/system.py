# app/routers/system.py
from __future__ import annotations

import os
import json
from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from app.build import BUILD_MARK

router = Router(name="system")

def _mode() -> str:
    return os.getenv("MODE", "web")

def _env() -> str:
    return os.getenv("ENV", "staging")

@router.message(CommandStart())
async def cmd_start(m: Message):
    await m.answer(
        "👋 Привет! Я Elaya HQ Bot.\n"
        "Доступные команды:\n"
        "• /status — состояние бота\n"
        "• /healthz — быстрый пинг\n"
        "• /webhookinfo — показать состояние вебхука\n"
    )

@router.message(Command("status"))
async def cmd_status(m: Message):
    await m.answer(
        "🧭 Status\n"
        f"• ENV: <b>{_env()}</b>\n"
        f"• MODE: <b>{_mode()}</b>\n"
        f"• BUILD: <code>{BUILD_MARK}</code>"
    )

@router.message(Command("healthz"))
async def cmd_healthz(m: Message):
    await m.answer("✅ ok")

@router.message(Command("webhookinfo"))
async def cmd_webhookinfo(m: Message):
    # Полезно при MODE=web: показывает реальный url/secret на стороне Telegram
    info = await m.bot.get_webhook_info()
    data = {
        "url": info.url,
        "has_custom_certificate": info.has_custom_certificate,
        "pending_update_count": info.pending_update_count,
        "ip_address": getattr(info, "ip_address", None),
        "allowed_updates": info.allowed_updates,
        "max_connections": info.max_connections,
        "last_error_date": getattr(info, "last_error_date", None),
        "last_error_message": getattr(info, "last_error_message", None),
    }
    pretty = json.dumps(data, ensure_ascii=False, indent=2)
    await m.answer(f"<code>{pretty}</code>")
