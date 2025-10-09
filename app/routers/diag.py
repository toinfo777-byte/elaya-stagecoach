# app/routers/diag.py
from __future__ import annotations

import hashlib
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from app.build import BUILD_MARK
from app.config import settings

router = Router(name="diag")

def _panic_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🏋️ Тренировка дня"), KeyboardButton(text="📈 Мой прогресс")],
            [KeyboardButton(text="🎭 Мини-кастинг"),   KeyboardButton(text="🧭 Путь лидера")],
            [KeyboardButton(text="💬 Помощь / FAQ"),   KeyboardButton(text="⚙️ Настройки")],
            [KeyboardButton(text="🔐 Политика"),       KeyboardButton(text="⭐ Расширенная версия")],
        ],
        resize_keyboard=True,
        is_persistent=True,
        input_field_placeholder="Диагностика: кнопки живые",
    )

@router.message(Command("build"))
async def cmd_build(m: Message):
    await m.answer(f"🧱 BUILD: <code>{BUILD_MARK}</code>")

@router.message(Command("who"))
async def cmd_who(m: Message):
    me = await m.bot.get_me()
    token_hash = hashlib.md5(settings.bot_token.encode()).hexdigest()[:8]
    await m.answer(
        "🤖 <b>Бот</b>\n"
        f"• username: @{me.username}\n"
        f"• id: <code>{me.id}</code>\n"
        f"• token-hash: <code>{token_hash}</code>"
    )

@router.message(Command("webhook"))
async def cmd_webhook(m: Message):
    info = await m.bot.get_webhook_info()
    # у aiogram v3 у объекта есть .url, .has_custom_certificate, .pending_update_count, .ip_address, .allowed_updates
    await m.answer(
        "🕸 <b>Webhook</b>\n"
        f"• url: <code>{getattr(info, 'url', '')}</code>\n"
        f"• pending: <code>{getattr(info, 'pending_update_count', 0)}</code>\n"
        f"• ip: <code>{getattr(info, 'ip_address', '')}</code>\n"
        f"• allowed: <code>{','.join(getattr(info, 'allowed_updates', []) or [])}</code>"
    )

@router.message(Command("panicmenu"))
async def cmd_panicmenu(m: Message):
    await m.answer("Диагностическое меню (reply-клава):", reply_markup=_panic_kb())

@router.message(Command("panicoff"))
async def cmd_panicoff(m: Message):
    await m.answer("Клавиатура скрыта", reply_markup=ReplyKeyboardRemove())

@router.message(Command("ping"))
async def cmd_ping(m: Message):
    await m.answer("pong 🟢")

@router.message(Command("logout"))
async def cmd_logout(m: Message):
    # ⚠️ После этого текущая long-polling сессия аннулируется с стороны Telegram.
    try:
        await m.bot.log_out()
        await m.answer("↪️ logOut выполнен (старые long-polling-сессии закрыты). Перезапусти процесс.")
    except Exception as e:
        await m.answer(f"❗ logOut ошибка: <code>{e}</code>")
