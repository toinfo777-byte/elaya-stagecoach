from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.utils.markdown import hcode

router = Router()

@router.message(Command("status"))
async def cmd_status(message: Message):
    await message.answer("🟢 HQ online: вебхук активен, ядро отвечает.")

@router.message(Command("webhookinfo"))
async def cmd_webhookinfo(message: Message):
    info = await message.bot.get_webhook_info()
    text = (
        "🔗 <b>Webhook info</b>\n"
        f"url: {hcode(info.url or '-')} \n"
        f"has_custom_certificate: {info.has_custom_certificate}\n"
        f"pending_update_count: {info.pending_update_count}\n"
        f"ip_address: {hcode(info.ip_address or '-')}\n"
        f"allowed_updates: {', '.join(info.allowed_updates or []) or '-'}"
    )
    await message.answer(text)
