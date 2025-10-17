from __future__ import annotations
import asyncio, os, html
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from app.control.admin import require_admin, NotAdminError
from app.control.utils import status_block
from app.control.notifier import notify_admins

router = Router(name="control")

# /status — показать базовое состояние
@router.message(Command("status"))
async def cmd_status(m: Message):
    await m.answer(f"📊 <b>Status</b>\n{status_block()}")

# /reload — мягкий рестарт процесса (Render сам поднимет заново)
@router.message(Command("reload"))
async def cmd_reload(m: Message):
    try:
        require_admin(m.from_user.id if m.from_user else None)
    except NotAdminError:
        return await m.answer("⛔ Команда только для админов.")
    await m.answer("♻️ Перезапускаюсь…")
    # даём Telegram отправить ответ, затем завершаем процесс
    async def _exit_later():
        await asyncio.sleep(0.7)
        raise SystemExit(0)
    asyncio.create_task(_exit_later())

# /notify_admins <текст> — ручная рассылка уведомления
@router.message(Command("notify_admins"))
async def cmd_notify_admins(m: Message):
    try:
        require_admin(m.from_user.id if m.from_user else None)
    except NotAdminError:
        return await m.answer("⛔ Команда только для админов.")

    # текст после команды
    raw = (m.text or "").split(maxsplit=1)
    payload = raw[1].strip() if len(raw) > 1 else ""
    if not payload:
        payload = "🔔 Ручное уведомление от администратора."

    # дополним статусом сборки/окружения
    body = f"{html.escape(payload)}\n\n—\n{status_block()}"

    delivered = await notify_admins(m.bot, body)
    if delivered == 0:
        return await m.answer("⚠️ Некому отправлять: проверь переменные ADMIN_IDS / ADMIN_ALERT_CHAT_ID.")
    await m.answer(f"✅ Уведомление отправлено ({delivered})")
