# app/routers/entrypoints.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

# экраны/функции
from app.routers.help import show_main_menu, show_privacy, show_settings
from app.routers.training import show_training_levels
from app.routers.progress import show_progress
# если позже добавишь кастинги/лидера — импортируй их view и добавь ниже

go_router = Router(name="entrypoints")

# ── единый вход в главное меню ────────────────────────────────────────────────
@go_router.message(StateFilter("*"), F.text.in_({"💬 Помощь", "Помощь", "❓ Помощь"}))
async def ep_help(msg: Message, state: FSMContext):
    await state.clear()
    await show_main_menu(msg)

# ── универсальные callback-и «go:*» из инлайн-меню ────────────────────────────
@go_router.callback_query(F.data == "go:menu")
async def ep_go_menu(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.answer()
    await show_main_menu(cb)

@go_router.callback_query(F.data == "go:training")
async def ep_go_training(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.answer()
    await show_training_levels(cb.message, state)

@go_router.callback_query(F.data == "go:progress")
async def ep_go_progress(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.answer()
    await show_progress(cb.message)

@go_router.callback_query(F.data == "go:privacy")
async def ep_go_privacy(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.answer()
    await show_privacy(cb)

@go_router.callback_query(F.data == "go:settings")
async def ep_go_settings(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.answer()
    await show_settings(cb)

# задел на будущее:
# @go_router.callback_query(F.data == "go:casting")  -> await show_casting(...)
# @go_router.callback_query(F.data == "go:leader")   -> await show_leader(...)
# @go_router.callback_query(F.data == "go:extended") -> await show_extended(...)
