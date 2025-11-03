from __future__ import annotations

import os
from aiogram import Router, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from aiogram.enums import ChatType

router = Router(name="hq_status")

# Разрешим и приват, и группы
ALLOWED_CHATS = {ChatType.PRIVATE, ChatType.GROUP, ChatType.SUPERGROUP}

def _status_lines() -> list[str]:
    env = os.getenv("ENV", os.getenv("ENVIRONMENT", "unknown"))
    build = os.getenv("BUILD_MARK", os.getenv("RENDER_GIT_COMMIT", "manual"))
    mode = os.getenv("MODE", "webhook")
    svc = os.getenv("RENDER_SERVICE_NAME", "elaya-stagecoach-web")
    return [
        "🛰 <b>HQ-сводка</b>",
        f"Env: <code>{env}</code>",
        f"Mode: <code>{mode}</code>",
        f"Build: <code>{build}</code>",
        f"Service: <code>{svc}</code>",
    ]

@router.message(F.chat.type.in_(ALLOWED_CHATS), Command("ping"))
async def cmd_ping(message: Message, _: CommandObject) -> None:
    await message.reply("pong 🟢")

@router.message(F.chat.type.in_(ALLOWED_CHATS), Command("healthz"))
async def cmd_healthz(message: Message, _: CommandObject) -> None:
    await message.reply("OK")

@router.message(F.chat.type.in_(ALLOWED_CHATS), Command("status"))
async def cmd_status(message: Message, _: CommandObject) -> None:
    text = "\n".join(_status_lines())
    await message.reply(text, parse_mode="HTML")

# поддержка адресации вида `/status@ElayaHQBot`
@router.message(
    F.chat.type.in_(ALLOWED_CHATS),
    F.text.regexp(r"^/(status|ping|healthz)@").as_("match"),
)
async def cmd_with_mention(message: Message, match) -> None:
    cmd = match.group(1)
    if cmd == "status":
        await cmd_status(message, CommandObject(command="status"))
    elif cmd == "ping":
        await cmd_ping(message, CommandObject(command="ping"))
    else:
        await cmd_healthz(message, CommandObject(command="healthz"))
