# app/bot/routers/help.py
from __future__ import annotations
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from app.keyboards.menu import main_menu

router = Router(name="help")

def _is_help(text: str) -> bool:
    if not text:
        return False
    t = text.strip().lower()
    # убираем частые эмодзи перед словом
    for prefix in ("💬", "❓", "🆘", "🗨️"):
        if t.startswith(prefix.lower()):
            t = t[len(prefix):].strip()
    return "помощ" in t  # покрывает помощь/помощь/помощники и т.п.

@router.message(Command("help"))
@router.message(F.text.func(lambda s: _is_help(s or "")))
async def help_entry(message: Message) -> None:
    text = (
        "🆘 <b>Помощь</b>\n\n"
        "Команды:\n"
        "/start — Начать / онбординг\n"
        "/menu — Открыть меню\n"
        "/training — Тренировка дня\n"
        "/progress — Мой прогресс\n"
        "/apply — Путь лидера (заявка)\n"
        "/casting — Мини-кастинг\n"
        "/privacy — Политика конфиденциальности\n"
        "/help — Помощь\n"
        "/premium — Расширенная версия\n"
        "/settings — Настройки"
    )
    await message.answer(text, reply_markup=main_menu())
