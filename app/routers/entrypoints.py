from __future__ import annotations

import importlib, logging
from typing import Awaitable, Iterable

from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery, Message,
    InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove,
)

log = logging.getLogger("entrypoints")
go_router = Router(name="entrypoints")

# ───────────────────────────── UI ─────────────────────────────
def _menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏋️ Тренировка дня",    callback_data="go:training")],
        [InlineKeyboardButton(text="🎭 Мини-кастинг",      callback_data="go:casting")],
        [InlineKeyboardButton(text="🧭 Путь лидера",       callback_data="go:leader")],
        [InlineKeyboardButton(text="📈 Мой прогресс",      callback_data="go:progress")],
        [InlineKeyboardButton(text="💬 Помощь / FAQ",      callback_data="go:help")],
        [InlineKeyboardButton(text="🔐 Политика",          callback_data="go:privacy")],
        [InlineKeyboardButton(text="⚙️ Настройки",         callback_data="go:settings")],
        [InlineKeyboardButton(text="⭐ Расширенная версия", callback_data="go:extended")],
    ])

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

async def _show_menu(obj: Message | CallbackQuery):
    # Всегда снимаем липкую reply-клаву и рисуем inline
    if isinstance(obj, CallbackQuery):
        await obj.answer()
        await obj.message.answer("·", reply_markup=ReplyKeyboardRemove())
        await obj.message.answer(MENU_TEXT, reply_markup=_menu_kb())
    else:
        await obj.answer("·", reply_markup=ReplyKeyboardRemove())
        await obj.answer(MENU_TEXT, reply_markup=_menu_kb())

# ─────────────────── Dynamic import helper ────────────────────
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

# ───────────────────────── Команды ────────────────────────────
@go_router.message(CommandStart(deep_link=False))
async def cmd_start(m: Message, state: FSMContext):
    await _show_menu(m)

@go_router.message(Command("menu"))
async def cmd_menu(m: Message, state: FSMContext):
    await _show_menu(m)

@go_router.message(Command("fixmenu"))
async def cmd_fixmenu(m: Message):
    await m.answer("Меню обновлено.", reply_markup=ReplyKeyboardRemove())
    await _show_menu(m)

@go_router.message(Command("help"))
async def cmd_help(m: Message):
    if not await _call_optional("app.routers.help", ("show_help",), m):
        await _show_menu(m)

@go_router.message(Command("privacy"))
async def cmd_privacy(m: Message):
    if not await _call_optional("app.routers.privacy", ("show_privacy","open_privacy"), m):
        await _show_menu(m)

@go_router.message(Command("settings"))
async def cmd_settings(m: Message):
    if not await _call_optional("app.routers.settings", ("show_settings","open_settings"), m):
        await _show_menu(m)

@go_router.message(Command("progress"))
async def cmd_progress(m: Message):
    if not await _call_optional("app.routers.progress", ("show_progress","open_progress"), m):
        await m.answer("📈 «Мой прогресс» временно недоступен.")

@go_router.message(Command("training"))
async def cmd_training(m: Message, state: FSMContext):
    if not await _call_optional("app.routers.training", ("show_training_levels","open_training","start_training"), m, state):
        await m.answer("🏋️ «Тренировка дня» временно недоступна.")

@go_router.message(Command("leader"))
async def cmd_leader(m: Message, state: FSMContext):
    if not await _call_optional("app.routers.leader", ("open_leader","show_leader","leader_entry","start_leader"), m, state):
        await m.answer("🧭 «Путь лидера» скоро будет доступен.")

@go_router.message(Command("casting"))
async def cmd_casting(m: Message, state: FSMContext):
    if not await _call_optional("app.routers.minicasting", ("open_minicasting","show_minicasting","mc_entry","start_minicasting"), m, state):
        await m.answer("🎭 «Мини-кастинг» скоро будет доступен.")

@go_router.message(Command("extended"))
async def cmd_extended(m: Message):
    if not await _call_optional("app.routers.extended", ("open_extended","show_extended","extended_entry"), m):
        await m.answer("⭐️ «Расширенная версия» — позже.")

@go_router.message(Command("ping"))
async def cmd_ping(m: Message): await m.answer("pong 🟢")

@go_router.message(Command("cancel"))
async def cmd_cancel(m: Message, state: FSMContext):
    await state.clear(); await m.answer("↩️ Сброс состояний."); await _show_menu(m)

# ─────────── Callback go:* (без catch-all, чтобы не глушить другие) ───────────
@go_router.callback_query(F.data == "go:menu")
async def cb_go_menu(cq: CallbackQuery): await _show_menu(cq)

@go_router.callback_query(F.data == "go:help")
async def cb_go_help(cq: CallbackQuery):
    await cq.answer()
    if not await _call_optional("app.routers.help", ("show_help",), cq):
        await _show_menu(cq)

@go_router.callback_query(F.data == "go:privacy")
async def cb_go_privacy(cq: CallbackQuery):
    await cq.answer()
    if not await _call_optional("app.routers.privacy", ("show_privacy","open_privacy"), cq):
        await _show_menu(cq)

@go_router.callback_query(F.data == "go:settings")
async def cb_go_settings(cq: CallbackQuery):
    await cq.answer()
    if not await _call_optional("app.routers.settings", ("show_settings","open_settings"), cq):
        await _show_menu(cq)

@go_router.callback_query(F.data == "go:progress")
async def cb_go_progress(cq: CallbackQuery):
    await cq.answer()
    if not await _call_optional("app.routers.progress", ("show_progress","open_progress"), cq.message):
        await cq.message.answer("📈 «Мой прогресс» временно недоступен.")

@go_router.callback_query(F.data == "go:training")
async def cb_go_training(cq: CallbackQuery, state: FSMContext):
    await cq.answer()
    if not await _call_optional("app.routers.training", ("show_training_levels","open_training","start_training"), cq.message, state):
        await cq.message.answer("🏋️ «Тренировка дня» временно недоступна.")

@go_router.callback_query(F.data == "go:leader")
async def cb_go_leader(cq: CallbackQuery, state: FSMContext):
    await cq.answer()
    if not await _call_optional("app.routers.leader", ("open_leader","show_leader","leader_entry","start_leader"), cq.message, state):
        await cq.message.answer("🧭 «Путь лидера» скоро будет доступен.")

@go_router.callback_query(F.data == "go:casting")
async def cb_go_casting(cq: CallbackQuery, state: FSMContext):
    await cq.answer()
    if not await _call_optional("app.routers.minicasting", ("open_minicasting","show_minicasting","mc_entry","start_minicasting"), cq.message, state):
        await cq.message.answer("🎭 «Мини-кастинг» скоро будет доступен.")

@go_router.callback_query(F.data == "go:extended")
async def cb_go_extended(cq: CallbackQuery):
    await cq.answer()
    if not await _call_optional("app.routers.extended", ("open_extended","show_extended","extended_entry"), cq):
        await cq.message.answer("⭐️ «Расширенная версия» — позже.")

# ───────── Перехват «липкой» reply-клавы (текстовые кнопки) ─────────
TXT_TO_GO = {
    "🏋️ Тренировка дня":  "go:training",
    "🎭 Мини-кастинг":    "go:casting",
    "🧭 Путь лидера":     "go:leader",
    "📈 Мой прогресс":    "go:progress",
    "💬 Помощь":          "go:help",
    "💬 Помощь / FAQ":    "go:help",
    "🔐 Политика":        "go:privacy",
    "⚙️ Настройки":       "go:settings",
    "⭐ Расширенная версия": "go:extended",
    "Меню":               "go:menu",
    "В меню":             "go:menu",
    "🏠 В меню":          "go:menu",
}

@go_router.message(F.text.in_(set(TXT_TO_GO.keys())))
async def txt_redirect(m: Message, state: FSMContext):
    # снимаем reply-клаву и перенаправляем в нужный раздел
    await m.answer("·", reply_markup=ReplyKeyboardRemove())
    target = TXT_TO_GO[m.text]
    if target == "go:menu":        await _show_menu(m); return
    if target == "go:help":        await cmd_help(m); return
    if target == "go:privacy":     await cmd_privacy(m); return
    if target == "go:settings":    await cmd_settings(m); return
    if target == "go:progress":    await cmd_progress(m); return
    if target == "go:training":    await cmd_training(m, state); return
    if target == "go:leader":      await _call_optional("app.routers.leader", ("open_leader","show_leader","leader_entry","start_leader"), m, state); return
    if target == "go:casting":     await _call_optional("app.routers.minicasting", ("open_minicasting","show_minicasting","mc_entry","start_minicasting"), m, state); return
    if target == "go:extended":    await _call_optional("app.routers.extended", ("open_extended","show_extended","extended_entry"), m); return
    await _show_menu(m)
