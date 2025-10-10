# app/routers/devops_sync.py
from __future__ import annotations
import asyncio, os
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router(name="devops_sync")

def _is_admin(uid: int) -> bool:
    raw = os.getenv("ADMIN_IDS", "")  # читаем из ADMIN_IDS в Render
    ids = {int(x) for x in raw.split(",") if x.strip().isdigit()}
    return uid in ids if ids else False


@router.message(Command("sync_status"))
async def sync_status(message: Message):
    """Команда /sync_status — синхронизирует штабные файлы с GitHub"""
    if not _is_admin(message.from_user.id):
        await message.reply("⛔ Доступ запрещён.")
        return

    note = await message.reply("🔄 Синхронизация штаба…")

    cmd = ["python", "tools/sync_status.py"]
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        out, err = await proc.communicate()
        out_text = out.decode().strip()
        err_text = err.decode().strip()

        if proc.returncode == 0:
            msg = "✅ Готово.\n" + (out_text or "Скрипт завершился без вывода.")
        else:
            msg = f"❌ Ошибка ({proc.returncode}).\n{err_text or out_text or 'no details'}"

        await note.edit_text(msg)
    except Exception as e:
        await note.edit_text(f"❌ Исключение при запуске: {e}")
