from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

# Импортируем ПУБЛИЧНЫЕ входы разделов
from app.routers.help import show_main_menu, show_privacy, show_settings
from app.routers.training import show_training_levels
from app.routers.minicasting import start_minicasting
from app.routers.progress import show_progress
from app.routers.leader import leader_entry  # новый «Путь лидера»

# Базовый роутер этого модуля
router = Router(name="entrypoints")
# 👉 алиасы сразу под созданием роутера
go_router = router
go = router

async def _to_menu(obj: Message | CallbackQuery, state: FSMContext):
    await state.clear()
    await show_main_menu(obj)

# ---------- СЛЭШ-КОМАНДЫ (из любого стейта) ----------
@go.message(StateFilter("*"), Command("menu"))
async def cmd_menu(m: Message, state: FSMContext):
    await _to_menu(m, state)

@go.message(StateFilter("*"), Command("training"))
async def cmd_training(m: Message, state: FSMContext):
    await state.clear()
    await show_training_levels(m)

@go.message(StateFilter("*"), Command("casting"))
async def cmd_casting(m: Message, state: FSMContext):
    await state.clear()
    await start_minicasting(m)

@go.message(StateFilter("*"), Command("leader"))
@go.message(StateFilter("*"), Command("apply"))   # алиас на новый «Путь лидера»
async def cmd_leader(m: Message, state: FSMContext):
    await state.clear()
    await leader_entry(m)

@go.message(StateFilter("*"), Command("progress"))
async def cmd_progress(m: Message, state: FSMContext):
    await state.clear()
    await show_progress(m)

@go.message(StateFilter("*"), Command("settings"))
async def cmd_settings(m: Message, state: FSMContext):
    await state.clear()
    await show_settings(m)

@go.message(StateFilter("*"), Command("privacy"))
async def cmd_privacy(m: Message, state: FSMContext):
    await state.clear()
    await show_privacy(m)

# ---------- ТЕКСТЫ из большой Reply-клавиатуры ----------
@go.message(StateFilter("*"), F.text.in_({"🏠 Меню", "Меню"}))
async def txt_menu(m: Message, state: FSMContext):
    await _to_menu(m, state)

@go.message(StateFilter("*"), F.text == "🏋️ Тренировка дня")
async def txt_training(m: Message, state: FSMContext):
    await state.clear()
    await show_training_levels(m)

@go.message(StateFilter("*"), F.text == "🎭 Мини-кастинг")
async def txt_casting(m: Message, state: FSMContext):
    await state.clear()
    await start_minicasting(m)

@go.message(StateFilter("*"), F.text == "🧭 Путь лидера")
async def txt_leader(m: Message, state: FSMContext):
    await state.clear()
    await leader_entry(m)

@go.message(StateFilter("*"), F.text == "📈 Мой прогресс")
async def txt_progress(m: Message, state: FSMContext):
    await state.clear()
    await show_progress(m)

@go.message(StateFilter("*"), F.text == "💬 Помощь")
async def txt_help(m: Message, state: FSMContext):
    await _to_menu(m, state)

@go.message(StateFilter("*"), F.text == "🔐 Политика")
async def txt_priv(m: Message, state: FSMContext):
    await state.clear()
    await show_privacy(m)

@go.message(StateFilter("*"), F.text == "⚙️ Настройки")
async def txt_settings(m: Message, state: FSMContext):
    await state.clear()
    await show_settings(m)

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

# ---------- Фоллбек: любой неизвестный клик -> меню ----------
@go.callback_query()
async def cb_fallback(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await _to_menu(cb, state)
