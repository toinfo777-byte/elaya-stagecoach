# app/routers/common.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.keyboards.reply import main_menu_kb

router = Router(name="common")

# Глобальный выход в меню — из ЛЮБОГО состояния
@router.message(StateFilter("*"), Command(commands={"menu", "start"}))
@router.message(StateFilter("*"), F.text.in_({"В меню", "Меню", "🏠 В меню"}))
async def go_menu(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer("Готово! Открываю меню.", reply_markup=main_menu_kb())
