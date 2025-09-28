from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
import re  # <-- добавили

# ... (всё что выше — без изменений)

# ---------- КОЛЛБЭКИ из инлайн-меню (go:*) ----------
MENU = {"go:menu", "menu", "to_menu", "home", "main_menu"}

@go.callback_query(StateFilter("*"), F.data.in_(MENU))
async def cb_menu(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await _to_menu(cb, state)

@go.callback_query(StateFilter("*"), F.data == "go:training")
async def cb_training(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.clear()
    await show_training_levels(cb)

@go.callback_query(StateFilter("*"), F.data == "go:casting")
async def cb_casting(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.clear()
    await start_minicasting(cb)

@go.callback_query(StateFilter("*"), F.data == "go:leader")
async def cb_leader(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.clear()
    await leader_entry(cb)

@go.callback_query(StateFilter("*"), F.data == "go:progress")
async def cb_progress(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.clear()
    await show_progress(cb)

@go.callback_query(StateFilter("*"), F.data == "go:privacy")
async def cb_privacy(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.clear()
    await show_privacy(cb)

@go.callback_query(StateFilter("*"), F.data == "go:settings")
async def cb_settings(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.clear()
    await show_settings(cb)

# ---------- Фоллбек ТОЛЬКО для неизвестных go:* ----------
_GO_PREFIX = re.compile(r"^go:")

@go.callback_query(StateFilter("*"), F.data.regexp(_GO_PREFIX))
async def cb_fallback_go(cb: CallbackQuery, state: FSMContext):
    """Любой неизвестный go:* отправляем в меню.
    Важно: НЕ ловим другие префиксы (leader:*, mc:*, settings:* и т.п.)."""
    await cb.answer()
    await _to_menu(cb, state)
