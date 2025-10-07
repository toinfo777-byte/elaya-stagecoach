from __future__ import annotations

import importlib
from typing import Awaitable, Iterable

from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.routers.help import show_main_menu, show_help, show_privacy, show_settings

try:
    from app.routers.training import show_training_levels as training_entry
except Exception:
    training_entry = None

try:
    from app.routers.progress import show_progress as progress_entry
except Exception:
    progress_entry = None

go_router = Router(name="entrypoints")


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


# ——— Команды ———
@go_router.message(CommandStart(deep_link=False))
async def cmd_start(m: Message, state: FSMContext):
    await show_main_menu(m)

@go_router.message(Command("menu"))
async def cmd_menu(m: Message, state: FSMContext):
    await show_main_menu(m)

@go_router.message(Command("help"))
async def cmd_help(m: Message):
    await show_help(m)

@go_router.message(Command("privacy"))
async def cmd_privacy(m: Message):
    if not await _call_optional("app.routers.privacy", ("show_privacy", "open_privacy"), m):
        await show_privacy(m)

@go_router.message(Command("settings"))
async def cmd_settings(m: Message):
    if not await _call_optional("app.routers.settings", ("show_settings", "open_settings"), m):
        await show_settings(m)

@go_router.message(Command("progress"))
async def cmd_progress(m: Message):
    if progress_entry:
        await progress_entry(m)
    elif not await _call_optional("app.routers.progress", ("show_progress", "open_progress"), m):
        await m.answer("📈 Раздел «Мой прогресс» временно недоступен.")

@go_router.message(Command("training"))
async def cmd_training(m: Message, state: FSMContext):
    if training_entry:
        await training_entry(m, state)
    elif not await _call_optional("app.routers.training",
                                  ("show_training_levels", "open_training", "start_training"),
                                  m, state):
        await m.answer("🏋️ Раздел «Тренировка дня» временно недоступен.")

@go_router.message(Command("leader"))
async def cmd_leader(m: Message, state: FSMContext):
    if not await _call_optional("app.routers.leader",
                                ("open_leader", "show_leader", "leader_entry", "start_leader"),
                                m, state):
        await m.answer("🧭 «Путь лидера» скоро будет доступен в этой сборке.")

@go_router.message(Command("casting"))
async def cmd_casting(m: Message, state: FSMContext):
    if not await _call_optional("app.routers.minicasting",
                                ("open_minicasting", "show_minicasting", "mc_entry", "start_minicasting"),
                                m, state):
        await m.answer("🎭 «Мини-кастинг» скоро будет доступен в этой сборке.")

@go_router.message(Command("extended"))
async def cmd_extended(m: Message):
    if not await _call_optional("app.routers.extended",
                                ("open_extended", "show_extended", "extended_entry"), m):
        await m.answer("⭐️ «Расширенная версия» появится после стабилизации dev-сборки.")

@go_router.message(Command("faq"))
async def cmd_faq(m: Message):
    if not await _call_optional("app.routers.faq", ("open_faq", "show_faq"), m):
        await show_help(m)

@go_router.message(Command("ping"))
async def cmd_ping(m: Message):
    await m.answer("pong 🟢")

@go_router.message(Command("healthz"))
async def cmd_healthz(m: Message):
    await m.answer("ok")

@go_router.message(Command("cancel"))
async def cmd_cancel(m: Message, state: FSMContext):
    await state.clear()
    await m.answer("↩️ Сброс состояний. Возвращаю в меню.")
    await show_main_menu(m)


# ——— Callback-навигация: go:* ———
@go_router.callback_query(F.data == "go:menu")
async def cb_go_menu(cq: CallbackQuery):
    await show_main_menu(cq)

@go_router.callback_query(F.data == "go:help")
async def cb_go_help(cq: CallbackQuery):
    await cq.answer()
    await show_help(cq)

@go_router.callback_query(F.data == "go:privacy")
async def cb_go_privacy(cq: CallbackQuery):
    await cq.answer()
    if not await _call_optional("app.routers.privacy", ("show_privacy", "open_privacy"), cq):
        await show_privacy(cq)

@go_router.callback_query(F.data == "go:settings")
async def cb_go_settings(cq: CallbackQuery):
    await cq.answer()
    if not await _call_optional("app.routers.settings", ("show_settings", "open_settings"), cq):
        await show_settings(cq)

@go_router.callback_query(F.data == "go:progress")
async def cb_go_progress(cq: CallbackQuery):
    await cq.answer()
    if progress_entry:
        await progress_entry(cq.message)
        return
    if not await _call_optional("app.routers.progress", ("show_progress", "open_progress"), cq.message):
        await cq.message.answer("📈 Раздел «Мой прогресс» временно недоступен.")

@go_router.callback_query(F.data == "go:training")
async def cb_go_training(cq: CallbackQuery, state: FSMContext):
    await cq.answer()
    if training_entry:
        await training_entry(cq.message, state)
        return
    if not await _call_optional("app.routers.training",
                                ("show_training_levels", "open_training", "start_training"),
                                cq.message, state):
        await cq.message.answer("🏋️ Раздел «Тренировка дня» временно недоступен.")

@go_router.callback_query(F.data == "go:leader")
async def cb_go_leader(cq: CallbackQuery, state: FSMContext):
    await cq.answer()
    if not await _call_optional("app.routers.leader",
                                ("open_leader", "show_leader", "leader_entry", "start_leader"),
                                cq.message, state):
        await cq.message.answer("🧭 «Путь лидера» скоро будет доступен в этой сборке.")

@go_router.callback_query(F.data == "go:casting")
async def cb_go_casting(cq: CallbackQuery, state: FSMContext):
    await cq.answer()
    if not await _call_optional("app.routers.minicasting",
                                ("open_minicasting", "show_minicasting", "mc_entry", "start_minicasting"),
                                cq.message, state):
        await cq.message.answer("🎭 «Мини-кастинг» скоро будет доступен в этой сборке.")

@go_router.callback_query(F.data == "go:extended")
async def cb_go_extended(cq: CallbackQuery):
    await cq.answer()
    if not await _call_optional("app.routers.extended",
                                ("open_extended", "show_extended", "extended_entry"), cq):
        await cq.message.answer("⭐️ «Расширенная версия» появится после стабилизации dev-сборки.")

# Перехватываем любые другие go:* — чтобы кнопка никогда не «молчала»
@go_router.callback_query(F.data.startswith("go:"))
async def cb_go_fallback(cq: CallbackQuery):
    await cq.answer()
    await cq.message.answer("⏳ Раздел на подключении. Открой пока «🏋️ Тренировка дня».")
