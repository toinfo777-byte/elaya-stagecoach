# app/routers/system.py
from datetime import datetime, timezone
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from app.config import settings

router = Router(name="system")

# отметка старта процесса бота
STARTED_AT = datetime.now(timezone.utc)

def _fmt_uptime() -> str:
    delta = datetime.now(timezone.utc) - STARTED_AT
    secs = int(delta.total_seconds())
    d, secs = divmod(secs, 86400)
    h, secs = divmod(secs, 3600)
    m, s = divmod(secs, 60)
    parts = []
    if d: parts.append(f"{d}d")
    if h: parts.append(f"{h}h")
    if m: parts.append(f"{m}m")
    parts.append(f"{s}s")
    return " ".join(parts)

@router.message(Command("health"))
async def health(m: Message):
    env = settings.env
    db = "sqlite" if "sqlite" in settings.db_url.lower() else "db"
    await m.answer(f"ok | env={env} | db={db} | uptime={_fmt_uptime()}")

@router.message(Command("version"))
async def version(m: Message):
    await m.answer("version=dev tmp")

@router.message(Command("whoami"))
async def whoami(m: Message):
    await m.answer(f"id={m.from_user.id} | chat={m.chat.id}")
