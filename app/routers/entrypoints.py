from __future__ import annotations

import importlib
from typing import Iterable, Awaitable, Dict

from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove,
)

go_router = Router(name="entrypoints_reply")

# ───────────────────────────── UI (reply-клава на 8 кнопок) ─────────────────────────────
def _reply_menu_kb() -> ReplyKeyboardMarkup:
    rows = [
        [KeyboardButton(text="🏋️ Тренировка дня"), KeyboardButton(text="📈 Мой прогресс")],
        [KeyboardButton(text="🎭 Мини-кастинг"),   KeyboardButton(text="🧭 Путь лидера")],
        [KeyboardButton(text="💬 Помощь / FAQ"),   KeyboardButton(text="⚙️ Настройки")],
        [KeyboardButton(text="🔐 Политика"),       KeyboardButton(text="⭐ Расширенная версия")],
    ]
    return ReplyKeyboardMarkup(
        keyboard=rows,
        resize_keyboard=True,
        is_persistent=True,
        input_field_placeholder="Выбери раздел…",
    )

MENU_TEXT = (
    "Команды и разделы: выбери нужное ⤵️\n\n"
    "🏋️ <b>Тренировка дня</b> — ежедневная рутина 5–15 мин.\n"
    "🎭 <b>Мини-кастинг</b> — быстрый чек 2–3 мин.\n"
    "🧭 <b>Путь лидера</b> — цель + микро-задание + заявка.\n"
    "📈 <b>Мой прогресс</b> — стрик и эпизоды за 7 дней.\n"
    "💬 <b>Помощь / FAQ</b> — ответы на частые вопросы.\n"
    "⚙️ <b>Настройки</b> — профиль.\n"
    "🔐 <b>Политика</b> — как храним и используем данные.\n"
    "⭐ <b>Расширенная версия</b> — скоро."
)

async def _show_menu(m: Message):
    await m.answer(MENU_TEXT, reply_markup=_reply_menu_kb())

# ───────────────────────────── динамический вызов ─────────────────────────────
async def _call_optional(module: str, candidates: Iterable[str], *args, **kwargs) -> bool:
    try:
        mod = importlib.import_module(module)
    except Exception:
        return False
    for name in candidates:
        fn = getattr(mod, name, None)
        if callable(fn):
            res = fn(*args, **kwargs)
            if isinstance(res, Awaitable):
                await res
            return True
    return False

# ───────────────────────────── команды ─────────────────────────────
@go_router.message(CommandStart(deep_link=False))
async def cmd_start(m: Message, state: FSMContext):
    await _show_menu(m)

@go_router.message(Command("menu"))
async def cmd_menu(m: Message, state: FSMContext):
    await _show_menu(m)

@go_router.message(Command("fixmenu"))
async def cmd_fixmenu(m: Message):
    await m.answer("Меню обновлено.", reply_markup=_reply_menu_kb())

@go_router.message(Command("help"))
async def cmd_help(m: Message):
    if not await _call_optional("app.routers.help", ("show_help",), m):
        await m.answer("💬 Раздел помощи обновим чуть позже.", reply_markup=_reply_menu_kb())

@go_router.message(Command("privacy"))
async def cmd_privacy(m: Message):
    if not await _call_optional("app.routers.privacy", ("show_privacy","open_privacy"), m):
        await m.answer("🔐 Политика будет опубликована перед релизом.", reply_markup=_reply_menu_kb())

@go_router.message(Command("settings"))
async def cmd_settings(m: Message):
    if not await _call_optional("app.routers.settings", ("show_settings","open_settings"), m):
        await m.answer("⚙️ Профиль скоро будет доступен.", reply_markup=_reply_menu_kb())

@go_router.message(Command("progress"))
async def cmd_progress(m: Message):
    if not await _call_optional("app.routers.progress", ("show_progress","open_progress"), m):
        await m.answer("📈 «Мой прогресс» временно недоступен.", reply_markup=_reply_menu_kb())

@go_router.message(Command("training"))
async def cmd_training(m: Message, state: FSMContext):
    if not await _call_optional("app.routers.training", ("show_training_levels","open_training","start_training"), m, state):
        await m.answer("🏋️ «Тренировка дня» временно недоступна.", reply_markup=_reply_menu_kb())

@go_router.message(Command("leader"))
async def cmd_leader(m: Message, state: FSMContext):
    if not await _call_optional("app.routers.leader", ("open_leader","show_leader","leader_entry","start_leader"), m, state):
        await m.answer("🧭 «Путь лидера» скоро будет доступен.", reply_markup=_reply_menu_kb())

@go_router.message(Command("casting"))
async def cmd_casting(m: Message, state: FSMContext):
    if not await _call_optional("app.routers.minicasting", ("open_minicasting","show_minicasting","mc_entry","start_minicasting"), m, state):
        await m.answer("🎭 «Мини-кастинг» скоро будет доступен.", reply_markup=_reply_menu_kb())

@go_router.message(Command("extended"))
async def cmd_extended(m: Message):
    if not await _call_optional("app.routers.extended", ("open_extended","show_extended","extended_entry"), m):
        await m.answer("⭐️ «Расширенная версия» — позже.", reply_markup=_reply_menu_kb())

@go_router.message(Command("ping"))
async def cmd_ping(m: Message): await m.answer("pong 🟢", reply_markup=_reply_menu_kb())

@go_router.message(Command("cancel"))
async def cmd_cancel(m: Message, state: FSMContext):
    await state.clear()
    await m.answer("↩️ Сброс состояний.", reply_markup=_reply_menu_kb())

# ───────────────────────────── текстовая навигация (reply-клава) ─────────────────────────────
TXT_TO_HANDLER: Dict[str, str] = {
    "🏋️ Тренировка дня":  "training",
    "📈 Мой прогресс":    "progress",
    "🎭 Мини-кастинг":    "casting",
    "🧭 Путь лидера":     "leader",
    "💬 Помощь / FAQ":    "help",
    "⚙️ Настройки":       "settings",
    "🔐 Политика":        "privacy",
    "⭐ Расширенная версия": "extended",
}

@go_router.message(F.text.in_(set(TXT_TO_HANDLER.keys())))
async def txt_menu_router(m: Message, state: FSMContext):
    t = TXT_TO_HANDLER[m.text]
    if t == "training":  await cmd_training(m, state);   return
    if t == "progress":  await cmd_progress(m);          return
    if t == "casting":   await cmd_casting(m, state);    return
    if t == "leader":    await cmd_leader(m, state);     return
    if t == "help":      await cmd_help(m);              return
    if t == "settings":  await cmd_settings(m);          return
    if t == "privacy":   await cmd_privacy(m);           return
    if t == "extended":  await cmd_extended(m);          return
    await _show_menu(m)
