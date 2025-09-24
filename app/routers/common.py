# app/routers/common.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from app.keyboards.reply import main_menu_kb

router = Router(name="common")

async def _to_menu_msg(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer("Готово! Открываю меню.", reply_markup=main_menu_kb())

# /menu, /start, /cancel и текстовые кнопки — из ЛЮБОГО состояния
@router.message(StateFilter("*"), Command({"menu", "start", "cancel"}))
@router.message(StateFilter("*"), F.text.in_({"В меню", "Меню", "🏠 В меню"}))
async def go_menu(msg: Message, state: FSMContext):
    # /start — короткое приветствие перед меню (не обязательно)
    if isinstance(msg, Message) and msg.text and msg.text.strip().lower() == "/start":
        await state.clear()
        await msg.answer("Привет! Я Элайя — тренер сцены. Помогу прокачать голос и уверенность.")
    await _to_menu_msg(msg, state)

# инлайн «в меню»
@router.callback_query(StateFilter("*"), F.data.in_({"go:menu", "to_menu"}))
async def cb_go_menu(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.answer()
    await cb.message.answer("Готово! Открываю меню.", reply_markup=main_menu_kb())
