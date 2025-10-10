from __future__ import annotations
import asyncio, os
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router(name="devops_sync")

def _is_admin(uid: int) -> bool:
    raw = os.getenv("BOT_ADMIN_IDS", "")
    ids = {int(x) for x in raw.split(",") if x.strip().isdigit()}
    return uid in ids if ids else False

@router.message(Command("sync_status"))
async def sync_status(message: Message):
    if not _is_admin(message.from_user.id):
        await message.reply("⛔ Доступ запрещён.")
        return

    note = await message.reply("🔄 Синхронизация штаба…")
    cmd = ["python", "tools/sync_status.py"]
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        out, err = await proc.communicate()
        if proc.returncode == 0:
            await note.edit_text("✅ Готово.\n" + (out.decode().strip() or ""))
        else:
            await note.edit_text(f"❌ Ошибка ({proc.returncode}).\n{(err.decode().strip() or out.decode().strip())}")
    except Exception as e:
        await note.edit_text(f"❌ Исключение при запуске: {e}")
