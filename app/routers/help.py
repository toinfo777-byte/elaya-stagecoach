# app/routers/help.py
from __future__ import annotations
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from app.ui.menu import show_main_menu

router = Router(name="help")

@router.message(Command("start"))
async def cmd_start(msg: Message):
    await show_main_menu(msg)

@router.message(Command("menu"))
async def cmd_menu(msg: Message):
    await show_main_menu(msg)

@router.message(Command("help"))
async def cmd_help(msg: Message):
    await msg.answer(
        "💬 Помощь / FAQ\n\n"
        "/menu — главное меню\n"
        "/levels — список тренировок\n"
        "/casting — мини-кастинг\n"
        "Если что-то не работает — напиши сюда."
    )

# На случай, если где-то в UI прилетает callback перехода в меню
@router.callback_query(F.data.in_({"go:menu", "menu:home"}))
async def cb_menu(cb: CallbackQuery):
    await cb.answer(cache_time=1)
    await show_main_menu(cb)
