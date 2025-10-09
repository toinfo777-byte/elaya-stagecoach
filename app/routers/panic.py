from __future__ import annotations
import logging
from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    Message, CallbackQuery,
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove,
)

router = Router(name="panic")
log = logging.getLogger("panic")

def _kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🏋️ Тренировка дня"), KeyboardButton(text="📈 Мой прогресс")],
            [KeyboardButton(text="🧭 Путь лидера"), KeyboardButton(text="🎭 Мини-кастинг")],
            [KeyboardButton(text="💬 Помощь / FAQ"), KeyboardButton(text="⚙️ Настройки")],
            [KeyboardButton(text="🔐 Политика"), KeyboardButton(text="⭐ Расширенная версия")],
        ],
        resize_keyboard=True,
        is_persistent=True,
        input_field_placeholder="Выбери раздел…",
    )

MENU = (
    "Команды и разделы: выбери нужное ⤵️\n\n"
    "🏋️ Тренировка дня — 5–15 мин\n"
    "📈 Мой прогресс — стрик/эпизоды\n"
    "🎭 Мини-кастинг • 🧭 Путь лидера\n"
    "💬 Помощь • ⚙️ Настройки • 🔐 Политика • ⭐ Расширенная"
)

async def _menu(m: Message):
    await m.answer("·", reply_markup=ReplyKeyboardRemove())
    await m.answer(MENU, reply_markup=_kb())

# ─── commands
@router.message(CommandStart(deep_link=False))
async def start(m: Message): await _menu(m)

@router.message(Command("menu"))
async def menu(m: Message): await _menu(m)

@router.message(Command("ping"))
async def ping(m: Message): await m.answer("pong 🟢", reply_markup=_kb())

# ─── «живые» текстовые кнопки (простые ответы, лишь бы был отклик)
@router.message(F.text.in_({
    "🏋️ Тренировка дня","📈 Мой прогресс","🧭 Путь лидера","🎭 Мини-кастинг",
    "💬 Помощь / FAQ","⚙️ Настройки","🔐 Политика","⭐ Расширенная версия"
}))
async def buttons(m: Message):
    await m.answer(f"✅ Ок: {m.text}\n(диагностический режим)", reply_markup=_kb())

# ─── callback’и любого вида — просто подтверждаем, чтобы увидеть, что доходят
@router.callback_query()
async def any_cb(cq: CallbackQuery):
    data = (cq.data or "").strip()
    log.info("panic callback: %r", data)
    await cq.answer(f"cb:{data[:32] or 'empty'}")
    await cq.message.answer(f"📥 Получен callback: <code>{data or 'empty'}</code>")

# ─── fallback: ЛЮБОЕ другое сообщение → меню
@router.message()
async def any_text(m: Message):
    await _menu(m)
