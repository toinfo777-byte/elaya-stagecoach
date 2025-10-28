from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.config import settings

router = Router(name="control")


def _is_admin(user_id: int) -> bool:
    return user_id in settings.ADMIN_IDS


@router.message(Command("control"))
async def cmd_control(message: Message) -> None:
    uid = message.from_user.id if message.from_user else 0
    if not _is_admin(uid):
        await message.answer("⛔️ Доступ запрещён.")
        return
    await message.answer("✅ Админ-панель (заглушка) доступна. Настройте позже реальные команды.")
