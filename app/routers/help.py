# app/routers/help.py
from __future__ import annotations
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router(name="help")

@router.message(Command("start", "menu"))
async def show_main_menu(m: Message):
    await m.answer(
        "Команды и разделы: выбери нужное ⤵️\n\n"
        "🏋️ Тренировка дня\n💬 Помощь / FAQ\n(остальные временно скрыты)"
    )

@router.message(Command("help", "faq"))
async def help_info(m: Message):
    await m.answer(
        "💬 Помощь / FAQ\n\n"
        "• /menu — главное меню\n"
        "• /levels — список тренировок\n"
        "• /casting — мини-кастинг\n\n"
        "Если что-то не работает — просто напиши сюда."
    )

__all__ = ["router", "show_main_menu"]
