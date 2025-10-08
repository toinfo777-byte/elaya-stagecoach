# app/routers/help.py
from __future__ import annotations

import importlib
from typing import Awaitable, Iterable

from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove,
)

help_router = Router(name="help")

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

async def _reply(obj: Message | CallbackQuery, text: str,
                 kb: InlineKeyboardMarkup | None = None,
                 drop_reply_kb: bool = True):
    if isinstance(obj, CallbackQuery):
        await obj.answer()
        if drop_reply_kb:
            await obj.message.answer("·", reply_markup=ReplyKeyboardRemove())
        return await obj.message.answer(text, reply_markup=kb)
    else:
        if drop_reply_kb:
            await obj.answer("·", reply_markup=ReplyKeyboardRemove())
        return await obj.answer(text, reply_markup=kb)

# ───────────────────────────── Texts ─────────────────────────────
async def show_main_menu(obj: Message | CallbackQuery):
    text = (
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
    await _reply(obj, text, _menu_kb())

async def show_help(obj: Message | CallbackQuery):
    text = (
        "💬 <b>Помощь / FAQ</b>\n\n"
        "— «🏋️ Тренировка дня» — старт здесь.\n"
        "— «📈 Мой прогресс» — стрик и эпизоды.\n"
        "— «🧭 Путь лидера» — заявка и шаги.\n\n"
        "Если что-то не работает — /ping."
    )
    await _reply(obj, text, _menu_kb(), drop_reply_kb=False)

async def show_privacy(obj: Message | CallbackQuery):
    await _reply(obj, "🔐 <b>Политика</b>\n\nДетали обновим перед релизом.", _menu_kb(), drop_reply_kb=False)

async def show_settings(obj: Message | CallbackQuery):
    await _reply(obj, "⚙️ <b>Настройки</b>\n\nПрофиль в разработке.", _menu_kb(), drop_reply_kb=False)

# ────────────────────── Dynamic import helper ─────────────────────
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

# ───────────────────────────── Commands ─────────────────────────────
@help_router.message(CommandStart(deep_link=False))
async def start_no_payload(m: Message, state: FSMContext):
    await show_main_menu(m)

@help_router.message(Command("menu"))
async def cmd_menu(m: Message, state: FSMContext):
    await show_main_menu(m)

@help_router.message(Command("help"))
async def cmd_help(m: Message):
    await show_help(m)

@help_router.message(Command("privacy"))
async def cmd_privacy(m: Message):
    if not await _call_optional("app.routers.privacy", ("show_privacy","open_privacy"), m):
        await show_privacy(m)

@help_router.message(Command("settings"))
async def cmd_settings(m: Message):
    if not await _call_optional("app.routers.settings", ("show_settings","open_settings"), m):
        await show_settings(m)

@help_router.message(Command("progress"))
async def cmd_progress(m: Message):
    if not await _call_optional("app.routers.progress", ("show_progress","open_progress"), m):
        await m.answer("📈 «Мой прогресс» временно недоступен.")

@help_router.message(Command("training"))
async def cmd_training(m: Message, state: FSMContext):
    if not await _call_optional("app.routers.training", ("show_training_levels","open_training","start_training"), m, state):
        await m.answer("🏋️ «Тренировка дня» временно недоступна.")

# ───────────────────── Callback: go:* (полная навигация) ─────────────────────
@help_router.callback_query(F.data == "go:menu")
async def cb_go_menu(cq: CallbackQuery):
    await show_main_menu(cq)

@help_router.callback_query(F.data == "go:help")
async def cb_go_help(cq: CallbackQuery):
    await show_help(cq)

@help_router.callback_query(F.data == "go:privacy")
async def cb_go_privacy(cq: CallbackQuery):
    if not await _call_optional("app.routers.privacy", ("show_privacy","open_privacy"), cq):
        await show_privacy(cq)

@help_router.callback_query(F.data == "go:settings")
async def cb_go_settings(cq: CallbackQuery):
    if not await _call_optional("app.routers.settings", ("show_settings","open_settings"), cq):
        await show_settings(cq)

@help_router.callback_query(F.data == "go:progress")
async def cb_go_progress(cq: CallbackQuery):
    # ожидает Message
    if not await _call_optional("app.routers.progress", ("show_progress","open_progress"), cq.message):
        await cq.message.answer("📈 «Мой прогресс» временно недоступен.")

@help_router.callback_query(F.data == "go:training")
async def cb_go_training(cq: CallbackQuery, state: FSMContext):
    # ожидает (Message, state)
    if not await _call_optional("app.routers.training", ("show_training_levels","open_training","start_training"), cq.message, state):
        await cq.message.answer("🏋️ «Тренировка дня» временно недоступна.")

@help_router.callback_query(F.data == "go:leader")
async def cb_go_leader(cq: CallbackQuery, state: FSMContext):
    if not await _call_optional("app.routers.leader", ("open_leader","show_leader","leader_entry","start_leader"), cq.message, state):
        await cq.message.answer("🧭 «Путь лидера» скоро будет доступен.")

@help_router.callback_query(F.data == "go:casting")
async def cb_go_casting(cq: CallbackQuery, state: FSMContext):
    if not await _call_optional("app.routers.minicasting", ("open_minicasting","show_minicasting","mc_entry","start_minicasting"), cq.message, state):
        await cq.message.answer("🎭 «Мини-кастинг» скоро будет доступен.")

@help_router.callback_query(F.data == "go:extended")
async def cb_go_extended(cq: CallbackQuery):
    if not await _call_optional("app.routers.extended", ("open_extended","show_extended","extended_entry"), cq):
        await cq.message.answer("⭐️ «Расширенная версия» — после стабилизации dev.")

# Fallback на любые go:*
@help_router.callback_query(F.data.startswith("go:"))
async def cb_go_fallback(cq: CallbackQuery):
    await cq.answer()
    await cq.message.answer("⏳ Раздел готовится. Попробуй «🏋️ Тренировка дня».", reply_markup=_menu_kb())

# ─────────────── Перехват «липкой» reply-клавы (текст) ───────────────
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

@help_router.message(F.text.in_(set(TXT_TO_GO.keys())))
async def txt_redirect(m: Message, state: FSMContext):
    # сняли липкую reply-клаву и маршрутизировали в нужный раздел
    go = TXT_TO_GO[m.text]
    await m.answer("·", reply_markup=ReplyKeyboardRemove())
    # эмулируем нажатие нужной go:* кнопки
    if go == "go:menu":
        await show_main_menu(m); return
    if go == "go:help":
        await show_help(m); return
    if go == "go:privacy":
        await cmd_privacy(m); return
    if go == "go:settings":
        await cmd_settings(m); return
    if go == "go:progress":
        await cmd_progress(m); return
    if go == "go:training":
        await cmd_training(m, state); return
    if go == "go:leader":
        await _call_optional("app.routers.leader", ("open_leader","show_leader","leader_entry","start_leader"), m, state); return
    if go == "go:casting":
        await _call_optional("app.routers.minicasting", ("open_minicasting","show_minicasting","mc_entry","start_minicasting"), m, state); return
    if go == "go:extended":
        await _call_optional("app.routers.extended", ("open_extended","show_extended","extended_entry"), m); return
    # если ничего — просто меню
    await show_main_menu(m)
