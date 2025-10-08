from __future__ import annotations

import importlib
import logging
from typing import Iterable, Awaitable

from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove,
)

router = Router(name="system")
log = logging.getLogger("system")

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
    """Снять липкую reply-клаву и показать меню из 8 инлайн-кнопок."""
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
@router.message(CommandStart(deep_link=False))
async def cmd_start(m: Message, state: FSMContext):
    await _show_menu(m)

@router.message(Command("menu"))
async def cmd_menu(m: Message, state: FSMContext):
    await _show_menu(m)

@router.message(Command("fixmenu"))
async def cmd_fixmenu(m: Message):
    await m.answer("Меню обновлено.", reply_markup=ReplyKeyboardRemove())
    await _show_menu(m)

@router.message(Command("ping"))
async def cmd_ping(m: Message):
    await m.answer("pong 🟢")

@router.message(Command("cancel"))
async def cmd_cancel(m: Message, state: FSMContext):
    await state.clear()
    await m.answer("↩️ Сброс состояний.")
    await _show_menu(m)

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
@router.message(F.text.in_(set(TXT_TO_GO.keys())))
async def txt_redirect(m: Message, state: FSMContext):
    await m.answer("·", reply_markup=ReplyKeyboardRemove())
    # эмулируем «нажатие» нужной go:* кнопки
    class _FakeCQ:
        def __init__(self, message, data): self.message, self.data = message, data
        async def answer(self): pass
    await cb_go_any(_FakeCQ(m, TXT_TO_GO[m.text]), state)

# ─────────── Callback go:* + общий лог каждого клика ───────────
@router.callback_query()
async def cb_any_log(cq: CallbackQuery):
    log.info("callback: %r", (cq.data or "").strip())

@router.callback_query(F.data.startswith("go:"))
async def cb_go_any(cq: CallbackQuery, state: FSMContext):
    data = (cq.data or "").strip()
    await cq.answer()  # убираем «крутилку» в клиенте
    log.info("go:* -> %s", data)

    if data == "go:menu":
        await _show_menu(cq); return

    if data == "go:training":
        # (Message, state)
        if await _call_optional("app.routers.training",
                                ("show_training_levels", "open_training", "start_training"),
                                cq.message, state):
            return
        await cq.message.answer("🏋️ «Тренировка дня» временно недоступна."); return

    if data == "go:progress":
        # (Message)
        if await _call_optional("app.routers.progress",
                                ("show_progress", "open_progress"),
                                cq.message):
            return
        await cq.message.answer("📈 «Мой прогресс» временно недоступен."); return

    if data == "go:leader":
        if await _call_optional("app.routers.leader",
                                ("open_leader","show_leader","leader_entry","start_leader"),
                                cq.message, state):
            return
        await cq.message.answer("🧭 «Путь лидера» скоро будет доступен."); return

    if data == "go:casting":
        if await _call_optional("app.routers.minicasting",
                                ("open_minicasting","show_minicasting","mc_entry","start_minicasting"),
                                cq.message, state):
            return
        await cq.message.answer("🎭 «Мини-кастинг» скоро будет доступен."); return

    if data == "go:help":
        if await _call_optional("app.routers.help", ("show_help",), cq):
            return
        # если отдельного help нет — оставляем в меню
        await _show_menu(cq); return

    if data == "go:privacy":
        if await _call_optional("app.routers.privacy", ("show_privacy","open_privacy"), cq):
            return
        await _show_menu(cq); return

    if data == "go:settings":
        if await _call_optional("app.routers.settings", ("show_settings","open_settings"), cq):
            return
        await _show_menu(cq); return

    if data == "go:extended":
        if await _call_optional("app.routers.extended", ("open_extended","show_extended","extended_entry"), cq):
            return
        await cq.message.answer("⭐️ «Расширенная версия» — позже."); return

    # запасной вариант
    await _show_menu(cq)
