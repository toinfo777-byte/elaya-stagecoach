# app/routers/panic.py
from __future__ import annotations
import os
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

router = Router(name="panic")

def _is_admin(uid: int) -> bool:
    raw = os.getenv("ADMIN_IDS", "")
    ids = {int(x) for x in raw.split(",") if x.strip().isdigit()}
    return uid in ids if ids else False

@router.message(Command("ping"))
async def cmd_ping(message: Message):
    await message.reply("pong 🟢")

@router.message(Command("panicmenu"))
async def cmd_panicmenu(message: Message):
    if not _is_admin(message.from_user.id):
        await message.reply("⛔ Доступ запрещён.")
        return
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🏋️ Тренировка дня"), KeyboardButton(text="📈 Мой прогресс")],
            [KeyboardButton(text="🧭 Путь лидера"), KeyboardButton(text="💬 Помощь / FAQ")],
            [KeyboardButton(text="⚙️ Настройки"), KeyboardButton(text="⭐️ Расширенная версия")],
            [KeyboardButton(text="🔒 Политика")]
        ],
        resize_keyboard=True
    )
    await message.reply("Диагностическая клавиатура включена", reply_markup=kb)

@router.message(Command("panicoff"))
async def cmd_panicoff(message: Message):
    if not _is_admin(message.from_user.id):
        await message.reply("⛔ Доступ запрещён.")
        return
    await message.reply("Диагностическая клавиатура скрыта", reply_markup=ReplyKeyboardRemove())
