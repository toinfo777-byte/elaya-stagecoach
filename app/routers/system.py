from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, CommandStart

from app.build import BUILD_MARK
from app.config import settings

router = Router(name="system")

@router.message(CommandStart())
async def cmd_start(m: Message):
    await m.answer(
        "🫶 Привет! Я HQ-бот Элайи.\n"
        "Доступные быстрые команды:\n"
        "• /status — состояние ядра\n"
        "• /healthz — быстрый пинг\n"
        "• /webhookinfo — информация о вебхуке"
    )

@router.message(Command("status"))
async def cmd_status(m: Message):
    await m.answer(
        f"🧭 DevOps-cycle\n"
        f"ENV: <b>{settings.ENV}</b>\n"
        f"MODE: <b>{settings.MODE}</b>\n"
        f"BUILD: <code>{BUILD_MARK}</code>"
    )

@router.message(Command("healthz"))
async def cmd_healthz(m: Message):
    await m.answer("✅ ok")

@router.message(Command("webhookinfo"))
async def cmd_webhookinfo(m: Message):
    info = await m.bot.get_webhook_info()
    txt = (
        "🔗 <b>Webhook info</b>\n"
        f"url: <code>{info.url or '-'}</code>\n"
        f"has_custom_certificate: {info.has_custom_certificate}\n"
        f"pending_update_count: {info.pending_update_count}\n"
        f"ip_address: {getattr(info, 'ip_address', '-')}\n"
        f"allowed_updates: {', '.join(info.allowed_updates or []) or '-'}"
    )
    await m.answer(txt)
