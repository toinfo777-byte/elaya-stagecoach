# app/routers/help.py
from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.keyboards.reply import main_menu_kb

help_router = Router(name="help")

async def show_main_menu(m: Message) -> None:
    """Единая точка вывода главного меню (используют /menu и онбординг)."""
    await m.answer(
        "Команды и разделы: выбери нужное ⤵️",
        reply_markup=main_menu_kb(),
    )

@help_router.message(Command("menu"))
async def cmd_menu(m: Message) -> None:
    await show_main_menu(m)

@help_router.message(Command("help", "faq"))
async def cmd_help(m: Message) -> None:
    await m.answer(
        "💬 Помощь / FAQ\n\n"
        "🏋️ «Тренировка дня» — старт здесь.\n"
        "📈 «Мой прогресс» — стрик и эпизоды.\n"
        "🧭 «Путь лидера» — заявка и шаги (скоро).\n"
        "Если что-то не работает — /ping."
    )

# Совместимость: некоторые места ждут переменную `router`
router = help_router
__all__ = ["help_router", "router", "show_main_menu"]
