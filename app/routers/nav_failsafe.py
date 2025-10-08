from __future__ import annotations

import importlib
import logging
from typing import Awaitable, Iterable

from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery, Message,
    InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove,
)

log = logging.getLogger("nav_failsafe")
router = Router(name="nav_failsafe")

# пробуем прямые входы (если доступны)
try:
    from app.routers.training import show_training_levels as training_entry  # (Message, FSMContext)
except Exception:
    training_entry = None
try:
    from app.routers.progress import show_progress as progress_entry  # (Message)
except Exception:
    progress_entry = None


# ── UI: меню на 8 кнопок ─────────────────────────────────────────────────────
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
    if isinstance(obj, CallbackQuery):
        await obj.answer()
        await obj.message.answer("·", reply_markup=ReplyKeyboardRemove())
        await obj.message.answer(MENU_TEXT, reply_markup=_menu_kb())
    else:
        await obj.answer("·", reply_markup=ReplyKeyboardRemove())
        await obj.answer(MENU_TEXT, reply_markup=_menu_kb())


# ── утилита динамического вызова ─────────────────────────────────────────────
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


# ── Команды (входы) ──────────────────────────────────────────────────────────
@router.message(CommandStart(deep_link=False))
async def start(m: Message, state: FSMContext):
    await _show_menu(m)

@router.message(Command("menu"))
async def menu(m: Message, state: FSMContext):
    await _show_menu(m)

@router.message(Command("fixmenu"))
async def fixmenu(m: Message):
    await m.answer("Меню обновлено.", reply_markup=ReplyKeyboardRemove())
    await _show_menu(m)

@router.message(Command("help"))
async def help_cmd(m: Message):
    if not await _call_optional("app.routers.help", ("show_help",), m):
        await _show_menu(m)

@router.message(Command("ping")))
async def ping(m: Message):
    await m.answer("pong 🟢")


# ── Callback: ЖЁСТКАЯ СТРАХОВКА для всех go:* ────────────────────────────────
@router.callback_query(F.data.startswith("go:"))
async def cb_go_any(cq: CallbackQuery, state: FSMContext):
    data = cq.data or ""
    log.info("failsafe go:* -> %s", data)
    await cq.answer()  # убираем «крутилку» в клиенте

    if data == "go:menu":
        await _show_menu(cq); return

    if data == "go:training":
        if training_entry:
            await training_entry(cq.message, state); return
        if await _call_optional("app.routers.training", ("show_training_levels","open_training","start_training"), cq.message, state):
            return
        await cq.message.answer("🏋️ «Тренировка дня» временно недоступна."); return

    if data == "go:progress":
        if progress_entry:
            await progress_entry(cq.message); return
        if await _call_optional("app.routers.progress", ("show_progress","open_progress"), cq.message):
            return
        await cq.message.answer("📈 «Мой прогресс» временно недоступен."); return

    if data == "go:leader":
        if await _call_optional("app.routers.leader", ("open_leader","show_leader","leader_entry","start_leader"), cq.message, state):
            return
        await cq.message.answer("🧭 «Путь лидера» скоро будет доступен."); return

    if data == "go:casting":
        if await _call_optional("app.routers.minicasting", ("open_minicasting","show_minicasting","mc_entry","start_minicasting"), cq.message, state):
            return
        await cq.message.answer("🎭 «Мини-кастинг» скоро будет доступен."); return

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

    if data == "go:help":
        if await _call_optional("app.routers.help", ("show_help",), cq):
            return
        await _show_menu(cq)


# ── Перехват «липкой» reply-клавы: текстовые кнопки ──────────────────────────
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
    # Снимаем липкую клаву и просто прокидываем в наш же обработчик
    go = TXT_TO_GO[m.text]
    await m.answer("·", reply_markup=ReplyKeyboardRemove())
    # имитируем нажатие callback-кнопки
    if go == "go:menu":
        await _show_menu(m); return
    class _FakeCQ:
        # минимальный адаптер под наши вызовы
        def __init__(self, message): self.message = message
        async def answer(self): pass
        data = go
    await cb_go_any(_FakeCQ(m), state)
