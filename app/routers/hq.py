from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove

from app.build import BUILD_MARK

router = Router(name="hq")

@router.message(Command("status"))
async def cmd_status(msg: Message):
    me = await msg.bot.get_me()
    await msg.answer(
        "🟢 DevOps-cycle · live\n"
        f"Bot: @{me.username}\n"
        f"Build: <code>{BUILD_MARK}</code>\n"
        "Status: ok ✅",
        reply_markup=ReplyKeyboardRemove()
    )

@router.message(Command("webhookinfo"))
async def cmd_webhookinfo(msg: Message):
    info = await msg.bot.get_webhook_info()
    txt = [
        "🔗 Webhook info",
        f"url: <code>{info.url or '–'}</code>",
        f"has_custom_certificate: {info.has_custom_certificate}",
        f"pending_update_count: {info.pending_update_count}",
        f"ip_address: {info.ip_address or '–'}",
        f"allowed_updates: {','.join(info.allowed_updates or []) or '–'}",
    ]
    await msg.answer("\n".join(txt), reply_markup=ReplyKeyboardRemove())

@router.message(Command("getme"))
async def cmd_getme(msg: Message):
    me = await msg.bot.get_me()
    await msg.answer(
        f"id: <code>{me.id}</code>\n"
        f"username: @{me.username}\n"
        f"name: {me.full_name}",
        reply_markup=ReplyKeyboardRemove()
    )

@router.message(Command("build"))
async def cmd_build(msg: Message):
    await msg.answer(f"Build: <code>{BUILD_MARK}</code>", reply_markup=ReplyKeyboardRemove())
