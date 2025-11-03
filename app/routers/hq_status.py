# app/routers/hq_status.py
from __future__ import annotations

import os
from datetime import datetime, timezone

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

router = Router(name="hq-public")

def _now_str() -> str:
    return datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")

@router.message(Command(commands={"ping"}) & F.chat.type.in_({"private", "group", "supergroup"}))
async def cmd_ping(msg: Message):
    await msg.reply(f"pong 🟢  {_now_str()}")

@router.message(Command(commands={"status"}) & F.chat.type.in_({"private", "group", "supergroup"}))
async def cmd_status(msg: Message):
    env = os.getenv("ENV", os.getenv("ENVIRONMENT", "unknown"))
    mode = os.getenv("MODE", "webhook")
    build = os.getenv("BUILD_MARK", os.getenv("RENDER_GIT_COMMIT", "manual"))
    await msg.reply(
        "\n".join(
            [
                "🧭 <b>HQ Status</b>",
                f"Env: <code>{env}</code>",
                f"Mode: <code>{mode}</code>",
                f"Build: <code>{build}</code>",
                f"Chat: <code>{msg.chat.type}</code>",
                f"Time: <code>{_now_str()}</code>",
            ]
        )
    )

@router.message(Command(commands={"hq"}) & F.chat.type.in_({"private", "group", "supergroup"}))
async def cmd_hq(msg: Message):
    await msg.reply("Штаб: онлайн. Выбирай команду: /status, /ping.")
