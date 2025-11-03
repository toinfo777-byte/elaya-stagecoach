from __future__ import annotations
import os
from datetime import datetime, timezone

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

router = Router(name="hq-status")

def _now() -> str:
    return datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")

@router.message(
    Command(commands={"ping"}) & F.chat.type.in_({"private", "group", "supergroup"})
)
async def cmd_ping(m: Message) -> None:
    await m.reply(f"pong 🟢 {_now()}")

@router.message(
    Command(commands={"status"}) & F.chat.type.in_({"private", "group", "supergroup"})
)
async def cmd_status(m: Message) -> None:
    env = os.getenv("ENV", os.getenv("ENVIRONMENT", "unknown"))
    mode = os.getenv("MODE", "web")
    build = os.getenv("RENDER_GIT_COMMIT", os.getenv("BUILD_MARK", "manual"))
    await m.reply(
        "🧭 <b>HQ Status</b>\n"
        f"Env: <code>{env}</code>\n"
        f"Mode: <code>{mode}</code>\n"
        f"Build: <code>{build}</code>\n"
        f"Chat: <code>{m.chat.type}</code>\n"
        f"Time: <code>{_now()}</code>"
    )
