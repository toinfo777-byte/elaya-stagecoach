from __future__ import annotations

import os
import platform
from datetime import datetime, timezone

from aiogram import Router, F, types
from aiogram.filters import Command, CommandStart

router = Router(name="hq_status")

# Разрешаем трейты для любых чатов (private/group/supergroup)
ALLOWED_CHAT_TYPES = {"private", "group", "supergroup"}


def _mk_status() -> str:
    env = os.getenv("ENV", os.getenv("ENVIRONMENT", "unknown"))
    mode = os.getenv("MODE", "webhook")
    build = os.getenv("BUILD_MARK", os.getenv("RENDER_GIT_COMMIT", "manual"))
    host = platform.node()

    now = datetime.now(timezone.utc).astimezone()
    lines = [
        f"🛰 <b>HQ-status</b>",
        f"<i>{now:%Y-%m-%d %H:%M:%S %Z}</i>",
        "",
        f"• Env: <code>{env}</code>",
        f"• Mode: <code>{mode}</code>",
        f"• Build: <code>{build}</code>",
        f"• Host: <code>{host}</code>",
    ]
    return "\n".join(lines)


@router.message(CommandStart(), F.chat.type.in_(ALLOWED_CHAT_TYPES))
async def on_start(message: types.Message) -> None:
    await message.reply(
        "Привет! Я HQ-бот Элайи. Доступные команды: /status, /ping, /healthz",
        disable_web_page_preview=True,
    )


# /status и /status@ElayaHQBot (упоминание игнорируется по умолчанию)
@router.message(Command(commands=["status"]), F.chat.type.in_(ALLOWED_CHAT_TYPES))
async def cmd_status(message: types.Message) -> None:
    await message.reply(_mk_status())


@router.message(Command(commands=["ping"]), F.chat.type.in_(ALLOWED_CHAT_TYPES))
async def cmd_ping(message: types.Message) -> None:
    await message.reply("pong 🟢")


@router.message(Command(commands=["healthz"]), F.chat.type.in_(ALLOWED_CHAT_TYPES))
async def cmd_healthz(message: types.Message) -> None:
    await message.reply("ok")


# На случай если Telegram присылает команду в виде текста (редкие клиенты)
@router.message(
    F.text.lower().in_({"/status", "/ping", "/healthz"})
    & F.chat.type.in_(ALLOWED_CHAT_TYPES)
)
async def text_fallback(message: types.Message) -> None:
    text = message.text.lower()
    if text == "/ping":
        await cmd_ping(message)
    elif text == "/healthz":
        await cmd_healthz(message)
    else:
        await cmd_status(message)
