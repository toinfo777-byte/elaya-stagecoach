# app/routers/help.py
from __future__ import annotations
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from app.keyboards.reply import main_menu_kb, BTN_HELP

help_router = Router(name="help")

async def show_main_menu(m: Message) -> None:
    await m.answer(
        "Команды и разделы: выбери нужное ⤵️",
        reply_markup=main_menu_kb()
    )

@help_router.message(Command("start", "menu"))
async def cmd_start(m: Message):
    await show_main_menu(m)

@help_router.message(F.text == BTN_HELP)
async def help_btn(m: Message):
    await m.answer(
        "Помощь / FAQ\n\n• /menu — главное меню\n• /levels — список тренингов\n• /casting — мини-кастинг\n\nЕсли что-то не работает — напиши сюда же.",
        reply_markup=main_menu_kb()
    )

# ✔ Совместимость: чтобы работало и 'from ... import router', и 'from ... import help_router'
router = help_router
__all__ = ["help_router", "router", "show_main_menu"]
