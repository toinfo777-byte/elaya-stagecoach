from __future__ import annotations
import hashlib
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.build import BUILD_MARK

router = Router(name="diag")


@router.message(Command("build"))
async def cmd_build(message: Message):
    await message.reply(f"BUILD: <code>{BUILD_MARK}</code>")


@router.message(Command("who"))
async def cmd_who(message: Message):
    bot = message.bot
    me = await bot.get_me()
    token_hash = hashlib.md5((await bot.get_token()).encode()).hexdigest()[:8]
    await message.reply(
        f"🤖 @{me.username} (ID: <code>{me.id}</code>)\n🔑 token-hash: <code>{token_hash}</code>"
    )


@router.message(Command("webhook"))
async def cmd_webhook(message: Message):
    info = await message.bot.get_webhook_info()
    url = info.url or "none"
    await message.reply(f"Webhook: <code>{url}</code>")


# 🔹 Диагностика чата — временная команда для получения chat_id
@router.message(Command("diag"))
async def cmd_diag(message: Message):
    chat = message.chat
    user = message.from_user
    # вывод в лог Render
    print(f"CHAT DEBUG → chat.id={chat.id}, title={chat.title}, user.id={user.id}, user={user.full_name}")
    # ответ в Telegram
    await message.answer(
        f"🏓 pong\n"
        f"<b>Chat:</b> <code>{chat.id}</code>\n"
        f"<b>User:</b> <code>{user.id}</code>\n"
        f"<b>Title:</b> {chat.title or '—'}"
    )
