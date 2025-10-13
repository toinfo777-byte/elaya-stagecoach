# app/routers/help.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message

from app.keyboards.reply import main_menu_kb

router = Router(name="help")

async def show_main_menu(msg: Message):
    await msg.answer("Команды и разделы: выбери нужное ⤵️", reply_markup=main_menu_kb())

@router.message(Command("menu"))
@router.message(Command("start"))
async def menu_cmd(msg: Message):
    await show_main_menu(msg)

@router.message(StateFilter("*"), F.text == "💬 Помощь / FAQ")
@router.message(Command("help"))
async def show_help(msg: Message):
    await msg.answer(
        "💬 <b>Помощь / FAQ</b>\n\n"
        "🏋️ «Тренировка дня» — старт здесь.\n"
        "📈 «Мой прогресс» — стрик и эпизоды за 7 дней.\n"
        "🧭 «Путь лидера» — заявка и шаги (скоро).\n\n"
        "Если что-то не работает — /ping.",
        reply_markup=main_menu_kb()
    )

__all__ = ["router", "show_main_menu"]
