from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.enums import ChatType
from aiogram.types import Message, ReplyKeyboardRemove

router = Router(name="entrypoints")

# /start и /menu — ТОЛЬКО в личке
@router.message(Command("start", "menu"), F.chat.type == ChatType.PRIVATE)
async def start_menu_private(m: Message) -> None:
    text = (
        "Команды и разделы: выбери нужное 🧭\n"
        "🏅 Тренировка дня — ежедневная рутина 5–15 мин.\n"
        "📈 Мой прогресс — стрик и эпизоды за 7 дней.\n"
        "🛰️ Мини-кастинг · 🧭 Путь лидера\n"
        "❓ Помощь / FAQ · ⚙️ Настройки\n"
        "🔐 Политика · ⭐️ Расширенная версия"
    )
    await m.answer(text, reply_markup=ReplyKeyboardRemove())


# /healthz — можно везде (для проверки), остальное — отрежет middleware
@router.message(Command("healthz"))
async def healthz_cmd(m: Message) -> None:
    await m.answer("ok ✅")
