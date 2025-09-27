# app/routers/entrypoints.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

# экраны/входы из профильных роутеров
from app.routers.help import show_main_menu, show_privacy, show_settings
from app.routers.training import show_training_levels
from app.routers.minicasting import start_minicasting
from app.routers.progress import show_progress
from app.routers.leader import leader_entry  # убедись, что функция существует

router = Router(name="entrypoints")

# --- утилита: получить Message и ACK для коллбэков ---
async def _msg(obj: Message | CallbackQuery) -> Message:
    if isinstance(obj, CallbackQuery):
        await obj.answer()
        return obj.message
    return obj

# --- СЛЭШ-КОМАНДЫ (работают в ЛЮБОМ состоянии) ---

@router.message(StateFilter("*"), Command("menu"))
async def cmd_menu(m: Message, state: FSMContext):
    await state.clear()
    await show_main_menu(m)

@router.message(StateFilter("*"), Command("training"))
async def cmd_training(m: Message, state: FSMContext):
    await state.clear()
    await show_training_levels(m, state)

@router.message(StateFilter("*"), Command("casting"))
async def cmd_casting(m: Message, state: FSMContext):
    await state.clear()
    await start_minicasting(m, state)

@router.message(StateFilter("*"), Command("leader"))
@router.message(StateFilter("*"), Command("apply"))  # алиас
async def cmd_leader(m: Message, state: FSMContext):
    await state.clear()
    await leader_entry(m)

@router.message(StateFilter("*"), Command("progress"))
async def cmd_progress(m: Message, state: FSMContext):
    await state.clear()
    await show_progress(m)

@router.message(StateFilter("*"), Command("settings"))
async def cmd_settings(m: Message, state: FSMContext):
    await state.clear()
    await show_settings(m)

@router.message(StateFilter("*"), Command("privacy"))
async def cmd_privacy(m: Message, state: FSMContext):
    await state.clear()
    await show_privacy(m)

# --- ALIAS-наборы для разных callback_data ---

MENU   = {"go:menu", "menu", "В_меню", "to_menu", "home", "main_menu"}
TRAIN  = {"go:training", "training", "training:start"}
LEADER = {"go:leader", "leader", "apply", "go:apply"}
CAST   = {"go:casting", "casting"}
PROGR  = {"go:progress", "progress"}
SETTS  = {"go:settings", "settings"}
PRIV   = {"go:privacy", "privacy", "policy"}

@router.callback_query(StateFilter("*"), F.data.in_(MENU))
async def cb_menu(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await show_main_menu(cb)

@router.callback_query(StateFilter("*"), F.data.in_(TRAIN))
async def cb_training(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await show_training_levels(await _msg(cb), state)

@router.callback_query(StateFilter("*"), F.data.in_(LEADER))
async def cb_leader(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await leader_entry(cb)

@router.callback_query(StateFilter("*"), F.data.in_(CAST))
async def cb_cast(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await start_minicasting(cb, state)

@router.callback_query(StateFilter("*"), F.data.in_(PROGR))
async def cb_progress(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await show_progress(cb)

@router.callback_query(StateFilter("*"), F.data.in_(SETTS))
async def cb_settings(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await show_settings(cb)

@router.callback_query(StateFilter("*"), F.data.in_(PRIV))
async def cb_privacy(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await show_privacy(cb)

# страховочный обработчик: любой неизвестный клик -> меню
@router.callback_query()
async def cb_fallback(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await show_main_menu(cb)

# Дополнительно: ловим текст с ReplyKeyboard (если используешь её)
@router.message(StateFilter("*"), F.text.in_({
    "🏋️ Тренировка дня", "🎭 Мини-кастинг", "🧭 Путь лидера",
    "📈 Мой прогресс", "💬 Помощь", "⚙️ Настройки", "🔐 Политика"
}))
async def reply_keyboard_aliases(m: Message, state: FSMContext):
    txt = (m.text or "").strip()
    await state.clear()
    if txt.startswith("🏋️"):
        return await show_training_levels(m, state)
    if txt.startswith("🎭"):
        return await start_minicasting(m, state)
    if txt.startswith("🧭"):
        return await leader_entry(m)
    if txt.startswith("📈"):
        return await show_progress(m)
    if txt.startswith("⚙️"):
        return await show_settings(m)
    if txt.startswith("🔐") or txt.lower().startswith("полит"):
        return await show_privacy(m)
    # «Помощь» — показываем главное меню
    await show_main_menu(m)

__all__ = ["router"]
