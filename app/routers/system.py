from __future__ import annotations

import importlib
from typing import Iterable, Awaitable, Dict
from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

router = Router(name="system")

# ——— UI: Reply-клавиатура 8 кнопок ———
def _reply_menu_kb() -> ReplyKeyboardMarkup:
    rows = [
        [KeyboardButton(text="🏋️ Тренировка дня"), KeyboardButton(text="📈 Мой прогресс")],
        [KeyboardButton(text="🎭 Мини-кастинг"),   KeyboardButton(text="🧭 Путь лидера")],
        [KeyboardButton(text="💬 Помощь / FAQ"),   KeyboardButton(text="⚙️ Настройки")],
        [KeyboardButton(text="🔐 Политика"),       KeyboardButton(text="⭐ Расширенная версия")],
    ]
    return ReplyKeyboardMarkup(
        keyboard=rows, resize_keyboard=True, is_persistent=True,
        input_field_placeholder="Выбери раздел…"
    )

MENU_TEXT = (
    "Команды и разделы: выбери нужное ⤵️\n\n"
    "🏋️ <b>Тренировка дня</b> — ежедневная рутина 5–15 мин.\n"
    "📈 <b>Мой прогресс</b> — стрик и эпизоды за 7 дней.\n"
    "🎭 <b>Мини-кастинг</b> • 🧭 <b>Путь лидера</b>\n"
    "💬 <b>Помощь / FAQ</b> • ⚙️ <b>Настройки</b>\n"
    "🔐 <b>Политика</b> • ⭐ <b>Расширенная версия</b>"
)

async def _show_menu(m: Message):
    await m.answer("·", reply_markup=ReplyKeyboardRemove())
    await m.answer(MENU_TEXT, reply_markup=_reply_menu_kb())

# ——— динамический вызов функции, если есть ———
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

# ——— команды ———
@router.message(CommandStart(deep_link=False))
async def cmd_start(m: Message, state: FSMContext): await _show_menu(m)

@router.message(Command("menu"))
async def cmd_menu(m: Message, state: FSMContext):  await _show_menu(m)

@router.message(Command("fixmenu"))
async def cmd_fixmenu(m: Message):                  await _show_menu(m)

@router.message(Command("ping"))
async def cmd_ping(m: Message):                      await m.answer("pong 🟢", reply_markup=_reply_menu_kb())

@router.message(Command("cancel"))
async def cmd_cancel(m: Message, state: FSMContext):
    await state.clear()
    await m.answer("↩️ Сброс состояний.", reply_markup=_reply_menu_kb())

# ——— текстовая навигация (reply-кнопки) ———
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

@router.message(F.text.in_(set(TXT_TO_HANDLER.keys())))
async def txt_menu_router(m: Message, state: FSMContext):
    t = TXT_TO_HANDLER[m.text]
    if t == "training":
        ok = await _call_optional("app.routers.training", ("show_training_levels","open_training","start_training"), m, state)
    elif t == "progress":
        ok = await _call_optional("app.routers.progress", ("show_progress","open_progress"), m)
    elif t == "casting":
        ok = await _call_optional("app.routers.minicasting", ("open_minicasting","show_minicasting","mc_entry","start_minicasting"), m, state)
    elif t == "leader":
        ok = await _call_optional("app.routers.leader", ("open_leader","show_leader","leader_entry","start_leader"), m, state)
    elif t == "help":
        ok = await _call_optional("app.routers.faq", ("open_faq","show_help","show_faq"), m)
    elif t == "settings":
        ok = await _call_optional("app.routers.settings", ("show_settings","open_settings"), m)
    elif t == "privacy":
        ok = await _call_optional("app.routers.privacy", ("show_privacy","open_privacy"), m)
    elif t == "extended":
        ok = await _call_optional("app.routers.extended", ("open_extended","show_extended","extended_entry"), m)
    else:
        ok = False
    if not ok:
        await _show_menu(m)

# ——— fallback: любое сообщение → меню ———
@router.message()
async def any_text_fallback(m: Message): await _show_menu(m)
