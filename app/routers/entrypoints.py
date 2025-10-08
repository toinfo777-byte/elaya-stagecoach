from __future__ import annotations

import importlib
from typing import Awaitable, Iterable

from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery, Message,
    InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove,
)

# Экран помощи/базовые тексты можно брать из help.py при наличии
try:
    from app.routers.help import show_help, show_privacy, show_settings
except Exception:
    show_help = show_privacy = show_settings = None  # fallback ниже

# Прямые входы, если доступны
try:
    from app.routers.training import show_training_levels as training_entry  # (Message, FSMContext)
except Exception:
    training_entry = None

try:
    from app.routers.progress import show_progress as progress_entry  # (Message)
except Exception:
    progress_entry = None

go_router = Router(name="entrypoints")


# ──────────────────────────────────────────────────────────────────────────────
# Меню — генерим прямо здесь (8 кнопок)
# ──────────────────────────────────────────────────────────────────────────────
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


async def _reply(obj: Message | CallbackQuery, text: str):
    """
    1) убираем старую reply-клаву (если была),
    2) отправляем меню как новое сообщение с inline-кнопками
    """
    if isinstance(obj, CallbackQuery):
        await obj.answer()
        # Сначала снимаем ReplyKeyboard, затем показываем меню
        await obj.message.answer("·", reply_markup=ReplyKeyboardRemove())
        return await obj.message.answer(text, reply_markup=_menu_kb())
    else:
        await obj.answer("·", reply_markup=ReplyKeyboardRemove())
        return await obj.answer(text, reply_markup=_menu_kb())


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
    await _reply(obj, text)


# ──────────────────────────────────────────────────────────────────────────────
# Утилита: безопасный динамический вызов
# ──────────────────────────────────────────────────────────────────────────────
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


# ──────────────────────────────────────────────────────────────────────────────
# Команды
# ──────────────────────────────────────────────────────────────────────────────
@go_router.message(CommandStart(deep_link=False))
async def cmd_start(m: Message, state: FSMContext):
    await show_main_menu(m)

@go_router.message(Command("menu"))
async def cmd_menu(m: Message, state: FSMContext):
    await show_main_menu(m)

# «выровнять» пользователей у кого залипла reply-клава
@go_router.message(Command("fixmenu"))
async def cmd_fixmenu(m: Message):
    await m.answer("Меню обновлено.", reply_markup=ReplyKeyboardRemove())
    await show_main_menu(m)

@go_router.message(Command("help"))
async def cmd_help(m: Message):
    if show_help:
        await show_help(m)
    else:
        await m.answer("💬 Помощь скоро будет обновлена.")
        await show_main_menu(m)

@go_router.message(Command("privacy"))
async def cmd_privacy(m: Message):
    if show_privacy:
        await show_privacy(m)
    else:
        if not await _call_optional("app.routers.privacy", ("show_privacy", "open_privacy"), m):
            await m.answer("🔐 Политика скоро будет обновлена.")
            await show_main_menu(m)

@go_router.message(Command("settings"))
async def cmd_settings(m: Message):
    if show_settings:
        await show_settings(m)
    else:
        if not await _call_optional("app.routers.settings", ("show_settings", "open_settings"), m):
            await m.answer("⚙️ Настройки в разработке.")
            await show_main_menu(m)

@go_router.message(Command("progress"))
async def cmd_progress(m: Message):
    if progress_entry:
        await progress_entry(m)
        return
    if not await _call_optional("app.routers.progress", ("show_progress", "open_progress"), m):
        await m.answer("📈 «Мой прогресс» временно недоступен.")

@go_router.message(Command("training"))
async def cmd_training(m: Message, state: FSMContext):
    if training_entry:
        await training_entry(m, state)
        return
    called = await _call_optional("app.routers.training",
                                  ("show_training_levels", "open_training", "start_training"),
                                  m, state)
    if not called:
        await m.answer("🏋️ «Тренировка дня» временно недоступна.")

@go_router.message(Command("leader"))
async def cmd_leader(m: Message, state: FSMContext):
    if not await _call_optional("app.routers.leader",
                                ("open_leader", "show_leader", "leader_entry", "start_leader"),
                                m, state):
        await m.answer("🧭 «Путь лидера» скоро будет доступен.")

@go_router.message(Command("casting"))
async def cmd_casting(m: Message, state: FSMContext):
    if not await _call_optional("app.routers.minicasting",
                                ("open_minicasting", "show_minicasting", "mc_entry", "start_minicasting"),
                                m, state):
        await m.answer("🎭 «Мини-кастинг» скоро будет доступен.")

@go_router.message(Command("extended"))
async def cmd_extended(m: Message):
    if not await _call_optional("app.routers.extended",
                                ("open_extended", "show_extended", "extended_entry"), m):
        await m.answer("⭐️ «Расширенная версия» — после стабилизации dev.")

@go_router.message(Command("faq"))
async def cmd_faq(m: Message):
    if not await _call_optional("app.routers.faq", ("open_faq", "show_faq"), m):
        await cmd_help(m)

@go_router.message(Command("ping"))
async def cmd_ping(m: Message):
    await m.answer("pong 🟢")

@go_router.message(Command("healthz"))
async def cmd_healthz(m: Message):
    await m.answer("ok")

@go_router.message(Command("cancel"))
async def cmd_cancel(m: Message, state: FSMContext):
    await state.clear()
    await m.answer("↩️ Сброс состояний.")
    await show_main_menu(m)


# ──────────────────────────────────────────────────────────────────────────────
# Callback go:*
# ──────────────────────────────────────────────────────────────────────────────
@go_router.callback_query(F.data == "go:menu")
async def cb_go_menu(cq: CallbackQuery):
    await show_main_menu(cq)

@go_router.callback_query(F.data == "go:help")
async def cb_go_help(cq: CallbackQuery):
    await cq.answer()
    if show_help:
        await show_help(cq)
    else:
        await cq.message.answer("💬 Помощь скоро будет обновлена.")
        await show_main_menu(cq)

@go_router.callback_query(F.data == "go:privacy")
async def cb_go_privacy(cq: CallbackQuery):
    await cq.answer()
    if show_privacy:
        await show_privacy(cq)
        return
    if not await _call_optional("app.routers.privacy", ("show_privacy", "open_privacy"), cq):
        await cq.message.answer("🔐 Политика скоро будет обновлена.")
        await show_main_menu(cq)

@go_router.callback_query(F.data == "go:settings")
async def cb_go_settings(cq: CallbackQuery):
    await cq.answer()
    if show_settings:
        await show_settings(cq)
        return
    if not await _call_optional("app.routers.settings", ("show_settings", "open_settings"), cq):
        await cq.message.answer("⚙️ Настройки в разработке.")
        await show_main_menu(cq)

@go_router.callback_query(F.data == "go:progress")
async def cb_go_progress(cq: CallbackQuery):
    await cq.answer()
    if progress_entry:
        await progress_entry(cq.message)
        return
    if not await _call_optional("app.routers.progress", ("show_progress", "open_progress"), cq.message):
        await cq.message.answer("📈 «Мой прогресс» временно недоступен.")

@go_router.callback_query(F.data == "go:training")
async def cb_go_training(cq: CallbackQuery, state: FSMContext):
    await cq.answer()
    if training_entry:
        await training_entry(cq.message, state)
        return
    called = await _call_optional("app.routers.training",
                                  ("show_training_levels", "open_training", "start_training"),
                                  cq.message, state)
    if not called:
        await cq.message.answer("🏋️ «Тренировка дня» временно недоступна.")

@go_router.callback_query(F.data == "go:leader")
async def cb_go_leader(cq: CallbackQuery, state: FSMContext):
    await cq.answer()
    called = await _call_optional("app.routers.leader",
                                  ("open_leader", "show_leader", "leader_entry", "start_leader"),
                                  cq.message, state)
    if not called:
        await cq.message.answer("🧭 «Путь лидера» скоро будет доступен.")

@go_router.callback_query(F.data == "go:casting")
async def cb_go_casting(cq: CallbackQuery, state: FSMContext):
    await cq.answer()
    called = await _call_optional("app.routers.minicasting",
                                  ("open_minicasting", "show_minicasting", "mc_entry", "start_minicasting"),
                                  cq.message, state)
    if not called:
        await cq.message.answer("🎭 «Мини-кастинг» скоро будет доступен.")

@go_router.callback_query(F.data == "go:extended")
async def cb_go_extended(cq: CallbackQuery):
    await cq.answer()
    called = await _call_optional("app.routers.extended",
                                  ("open_extended", "show_extended", "extended_entry"),
                                  cq)
    if not called:
        await cq.message.answer("⭐️ «Расширенная версия» — после стабилизации dev.")

# Последний перехватчик на всякий случай
@go_router.callback_query(F.data.startswith("go:"))
async def cb_go_fallback(cq: CallbackQuery):
    await cq.answer()
    await cq.message.answer("⏳ Раздел готовится. Открой пока «🏋️ Тренировка дня».")
