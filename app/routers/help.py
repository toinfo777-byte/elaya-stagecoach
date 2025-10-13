# app/routers/help.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery

from app.keyboards.reply import main_menu_kb

router = Router(name="help")

MENU_TEXT = (
    "Команды и разделы: выбери нужное ⤵️\n\n"
    "🏋️ Тренировка дня — ежедневная рутина 5–15 мин.\n"
    "🎯 Мини-кастинг — быстрый чек 2–3 мин.\n"
    "🧭 Путь лидера — цель + микро-задание + заявка.\n"
    "📈 Мой прогресс — стрик и эпизоды за 7 дней.\n"
    "💬 Помощь / FAQ — ответы на частые вопросы.\n"
    "⚙️ Настройки — профиль.\n"
    "🔐 Политика — как храним и используем данные.\n"
    "⭐️ Расширенная версия — скоро."
)

async def show_main_menu(target: Message | CallbackQuery) -> None:
    """Публичная функция — показать главное меню (используют онбординг/entry)."""
    if isinstance(target, CallbackQuery):
        await target.answer()
        m = target.message
    else:
        m = target
    await m.answer(MENU_TEXT, reply_markup=main_menu_kb())

# /start и /menu ведут в одно место
@router.message(StateFilter("*"), Command("start", "menu"))
async def cmd_start_menu(msg: Message):
    await show_main_menu(msg)

# /help — краткая подсказка + меню
@router.message(StateFilter("*"), Command("help"))
async def cmd_help(msg: Message):
    await msg.answer("Если что-то не работает — /ping. Ниже разделы:")
    await show_main_menu(msg)

# На всякий — колбэк из других экранов «🏠 В меню»
@router.callback_query(StateFilter("*"), F.data == "go:menu")
async def go_menu(cq: CallbackQuery):
    await show_main_menu(cq)

# Алиас под старый импорт в main.py
help_router = router

__all__ = ["router", "help_router", "show_main_menu"]
