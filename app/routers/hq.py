from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.build import BUILD_MARK

router = Router(name="hq")

@router.message(Command("status"))
async def cmd_status(msg: Message):
    me = await msg.bot.get_me()
    await msg.answer(
        "🧭 DevOps-cycle · live\n"
        f"Bot: @{me.username}\n"
        f"Build: <code>{BUILD_MARK}</code>\n"
        "Status: ok ✅"
    )

@router.message(Command("webhookinfo"))
async def cmd_webhookinfo(msg: Message):
    info = await msg.bot.get_webhook_info()
    txt = [
        f"url: <code>{info.url or '—'}</code>",
        f"pending: {info.pending_update_count}",
        f"ip_address: {getattr(info, 'ip_address', '—')}",
        f"has_cert: {getattr(info, 'has_custom_certificate', False)}",
        f"max_connections: {getattr(info, 'max_connections', '—')}",
        f"allowed_updates: {', '.join(info.allowed_updates or []) or '—'}",
    ]
    await msg.answer("Webhook info:\n" + "\n".join(txt))
