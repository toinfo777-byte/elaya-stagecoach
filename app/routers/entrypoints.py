from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.enums import ChatType

router = Router(name="entrypoints")

# --- конструктор главного меню (только для приватных чатов)
def main_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [KeyboardButton(text="🏋️ Тренировка дня"), KeyboardButton(text="📈 Мой прогресс")],
            [KeyboardButton(text="🚀 Путь лидера"), KeyboardButton(text="⚙️ Настройки")],
            [KeyboardButton(text="💬 Помощь / FAQ"), KeyboardButton(text="⭐ Расширенная версия")],
            [KeyboardButton(text="📜 Политика")],
        ],
    )

# ===================== PRIVATES =====================

@router.message(CommandStart(), F.chat.type == ChatType.PRIVATE)
async def start_private(m: Message) -> None:
    await m.answer(
        "Команды и разделы: выбери нужное 🧭",
        reply_markup=main_menu_kb(),
    )

@router.message(Command("menu"), F.chat.type == ChatType.PRIVATE)
async def menu_private(m: Message) -> None:
    await m.answer(
        "Команды и разделы: выбери нужное 🧭",
        reply_markup=main_menu_kb(),
    )

# ===================== GROUPS / SUPERGROUPS =====================

# В группах и супергруппах /start и /menu НЕ показывают клавиатуру
@router.message((CommandStart() | Command("menu")), F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}))
async def menu_group(m: Message) -> None:
    # убираем залипшую клавиатуру, если она была
    await m.answer(
        "Я работаю в личке. Откройте меня: @ElayaDevTrainerBot или @ElayaStagingBot",
        reply_markup=ReplyKeyboardRemove(remove_keyboard=True),
    )
