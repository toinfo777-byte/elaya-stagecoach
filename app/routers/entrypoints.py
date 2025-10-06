from __future__ import annotations

import re
from typing import Any, Awaitable, Callable

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from app.routers.help import show_main_menu, show_privacy, show_settings
from app.routers.training import show_training_levels
from app.routers.minicasting import start_minicasting
from app.routers.progress import show_progress
from app.routers.leader import leader_entry
from app.routers.faq import show_faq_root

router = Router(name="entrypoints")
go_router = router
go = router
__all__ = ["router", "go_router", "go"]

# ── Безопасные вызовы + страховка в меню ─────────────────────────────────────

async def _safe_call(
    fn: Callable[..., Awaitable[Any]],
    obj: Message | CallbackQuery,
    state: FSMContext,
) -> Any:
    try:
        return await fn(obj, state)   # type: ignore[misc]
    except TypeError:
        return await fn(obj)          # type: ignore[misc]

async def _to_menu(obj: Message | CallbackQuery, state: FSMContext):
    try:
        await state.clear()
    except Exception:
        pass
    await show_main_menu(obj)

# ── Healthcheck ──────────────────────────────────────────────────────────────

@go.message(Command("ping"))
async def cmd_ping(m: Message):
    await m.answer("pong 🟢")

# ── Слэш-команды (из любого состояния) ───────────────────────────────────────

@go.message(StateFilter("*"), Command("start"))
async def cmd_start(m: Message, state: FSMContext):
    await _to_menu(m, state)

@go.message(StateFilter("*"), Command("menu"))
async def cmd_menu(m: Message, state: FSMContext):
    await _to_menu(m, state)

@go.message(StateFilter("*"), Command("cancel"))
async def cmd_cancel(m: Message, state: FSMContext):
    await _to_menu(m, state)

@go.message(StateFilter("*"), Command("help"))
async def cmd_help(m: Message, state: FSMContext):
    await state.clear()
    await show_faq_root(m)

@go.message(StateFilter("*"), Command("training"))
async def cmd_training(m: Message, state: FSMContext):
    try:
        await state.clear()
        await _safe_call(show_training_levels, m, state)
    except Exception:
        await _to_menu(m, state)

@go.message(StateFilter("*"), Command("casting"))
async def cmd_casting(m: Message, state: FSMContext):
    try:
        await state.clear()
        await _safe_call(start_minicasting, m, state)
    except Exception:
        await _to_menu(m, state)

@go.message(StateFilter("*"), Command("leader"))
@go.message(StateFilter("*"), Command("apply"))
async def cmd_leader(m: Message, state: FSMContext):
    try:
        await state.clear()
        await _safe_call(leader_entry, m, state)
    except Exception:
        await _to_menu(m, state)

@go.message(StateFilter("*"), Command("progress"))
async def cmd_progress(m: Message, state: FSMContext):
    try:
        await state.clear()
        await _safe_call(show_progress, m, state)
    except Exception:
        await _to_menu(m, state)

@go.message(StateFilter("*"), Command("settings"))
async def cmd_settings_cmd(m: Message, state: FSMContext):
    try:
        await state.clear()
        await _safe_call(show_settings, m, state)
    except Exception:
        await _to_menu(m, state)

@go.message(StateFilter("*"), Command("privacy"))
async def cmd_privacy_cmd(m: Message, state: FSMContext):
    try:
        await state.clear()
        await _safe_call(show_privacy, m, state)
    except Exception:
        await _to_menu(m, state)

# ── Тексты (если где-то используется reply-клава) ────────────────────────────

@go.message(StateFilter("*"), F.text.in_({"🏠 Меню", "Меню", "В меню", "🏠 В меню"}))
async def txt_menu(m: Message, state: FSMContext):
    await _to_menu(m, state)

@go.message(StateFilter("*"), F.text == "📈 Мой прогресс")
async def txt_progress(m: Message, state: FSMContext):
    try:
        await state.clear()
        await _safe_call(show_progress, m, state)
    except Exception:
        await _to_menu(m, state)

@go.message(StateFilter("*"), F.text == "🏋️ Тренировка дня")
async def txt_training(m: Message, state: FSMContext):
    try:
        await state.clear()
        await _safe_call(show_training_levels, m, state)
    except Exception:
        await _to_menu(m, state)

@go.message(StateFilter("*"), F.text == "🎭 Мини-кастинг")
async def txt_casting(m: Message, state: FSMContext):
    try:
        await state.clear()
        await _safe_call(start_minicasting, m, state)
    except Exception:
        await _to_menu(m, state)

@go.message(StateFilter("*"), F.text == "🧭 Путь лидера")
async def txt_leader(m: Message, state: FSMContext):
    try:
        await state.clear()
        await _safe_call(leader_entry, m, state)
    except Exception:
        await _to_menu(m, state)

@go.message(StateFilter("*"), F.text == "⚙️ Настройки")
async def txt_settings(m: Message, state: FSMContext):
    try:
        await state.clear()
        await _safe_call(show_settings, m, state)
    except Exception:
        await _to_menu(m, state)

@go.message(StateFilter("*"), F.text == "🔐 Политика")
async def txt_priv(m: Message, state: FSMContext):
    try:
        await state.clear()
        await _safe_call(show_privacy, m, state)
    except Exception:
        await _to_menu(m, state)

@go.message(StateFilter("*"), F.text == "💬 Помощь" )
async def txt_help_text(m: Message, state: FSMContext):
    await state.clear()
    await show_faq_root(m)

# ── Инлайн-кнопки go:* ───────────────────────────────────────────────────────

MENU = {"go:menu", "menu", "to_menu", "home", "main_menu"}

@go.callback_query(StateFilter("*"), F.data.in_(MENU))
async def cb_menu(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await _to_menu(cb, state)

@go.callback_query(StateFilter("*"), F.data == "go:training")
async def cb_training(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    try:
        await state.clear()
        await _safe_call(show_training_levels, cb, state)
    except Exception:
        await _to_menu(cb, state)

@go.callback_query(StateFilter("*"), F.data == "go:casting")
async def cb_casting(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    try:
        await state.clear()
        await _safe_call(start_minicasting, cb, state)
    except Exception:
        await _to_menu(cb, state)

@go.callback_query(StateFilter("*"), F.data == "go:leader")
async def cb_leader(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    try:
        await state.clear()
        await _safe_call(leader_entry, cb, state)
    except Exception:
        await _to_menu(cb, state)

@go.callback_query(StateFilter("*"), F.data == "go:progress")
async def cb_progress(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    try:
        await state.clear()
        await _safe_call(show_progress, cb, state)
    except Exception:
        await _to_menu(cb, state)

@go.callback_query(StateFilter("*"), F.data == "go:settings")
async def cb_settings(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    try:
        await state.clear()
        await _safe_call(show_settings, cb, state)
    except Exception:
        await _to_menu(cb, state)

@go.callback_query(StateFilter("*"), F.data == "go:privacy")
async def cb_privacy(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    try:
        await state.clear()
        await _safe_call(show_privacy, cb, state)
    except Exception:
        await _to_menu(cb, state)

@go.callback_query(StateFilter("*"), F.data == "go:help")
async def cb_help(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.clear()
    await show_faq_root(cb)

# Фоллбек: любые неизвестные go:* → в меню
_GO_PREFIX = re.compile(r"^go:")
@go.callback_query(StateFilter("*"), F.data.regexp(_GO_PREFIX))
async def cb_fallback_go(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await _to_menu(cb, state)
