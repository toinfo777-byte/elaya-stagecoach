# app/routers/common.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from app.keyboards.reply import main_menu_kb

router = Router(name="common")

async def _open_menu(msg: Message, state: FSMContext, greet: bool = False):
    await state.clear()
    if greet:
        await msg.answer("Привет! Я Элайя — тренер сцены. Помогу прокачать голос и уверенность.")
    await msg.answer("Готово! Открываю меню.", reply_markup=main_menu_kb())

# ✅ один хендлер на несколько команд — корректный синтаксис
@router.message(StateFilter("*"), Command(commands=["menu", "start", "cancel"]))
async def menu_start_cancel(message: Message, state: FSMContext):
    cmd = (message.text or "").lstrip("/").split()[0].lower()
    await _open_menu(message, state, greet=(cmd == "start"))

# текстовые кнопки «в меню»
@router.message(StateFilter("*"), F.text.in_({"В меню", "Меню", "🏠 В меню"}))
async def text_to_menu(message: Message, state: FSMContext):
    await _open_menu(message, state)

# инлайн «в меню» из callback’ов (добавили core:menu)
@router.callback_query(StateFilter("*"), F.data.in_({"go:menu", "to_menu", "core:menu"}))
async def cb_to_menu(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.answer()
    await cb.message.answer("Готово! Открываю меню.", reply_markup=main_menu_kb())
