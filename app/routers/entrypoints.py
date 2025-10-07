from __future__ import annotations

import importlib
from typing import Awaitable, Callable, Iterable, Optional

from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

# Экран меню и базовые экраны берём из help.py
from app.routers.help import show_main_menu, show_help, show_privacy, show_settings

# Точки входа в тренировки/прогресс — используем прямые функции, если есть
try:
    from app.routers.training import show_training_levels as training_entry  # expects (Message, FSMContext)
except Exception:
    training_entry = None  # подстрахуемся: вызовем динамически

try:
    from app.routers.progress import show_progress as progress_entry  # expects (Message)
except Exception:
    progress_entry = None

go_router = Router(name="entrypoints")


# ──────────────────────────────────────────────────────────────────────────────
# Вспомогательные динамические вызовы (не ломают архитектуру, если сигнатуры разные)
# ──────────────────────────────────────────────────────────────────────────────
async def _call_optional(module: str, candidates: Iterable[str], *args, **kwargs) -> bool:
    """
    Пытаемся импортировать модуль и вызвать первую найденную функцию из candidates.
    Возвращаем True, если вызов состоялся, иначе False.
    """
    try:
        mod = importlib.import_module(module)
    except Exception:
        return False
    for name in candidates:
        func = getattr(mod, name, None)
        if callable(func):
            try:
                res = func(*args, **kwargs)
                if isinstance(res, Awaitable):
                    await res
                return True
            except Exception:
                # мягко гасим, чтобы не ронять поток
                return False
    return False


# ──────────────────────────────────────────────────────────────────────────────
# Команды (текстовые)
# ──────────────────────────────────────────────────────────────────────────────
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
    # сначала пробуем модуль privacy
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
    else:
        # пробуем динамически
        if not await _call_optional("app.routers.progress", ("show_progress", "open_progress"), m):
            await m.answer("📈 Раздел «Мой прогресс» временно недоступен.")


@go_router.message(Command("training"))
async def cmd_training(m: Message, state: FSMContext):
    if training_entry:
        await training_entry(m, state)
    else:
        # пробуем динамически
        called = await _call_optional("app.routers.training",
                                      ("show_training_levels", "open_training", "start_training"),
                                      m, state)
        if not called:
            await m.answer("🏋️ Раздел «Тренировка дня» временно недоступен.")


@go_router.message(Command("leader"))
async def cmd_leader(m: Message, state: FSMContext):
    called = await _call_optional("app.routers.leader",
                                  ("open_leader", "show_leader", "leader_entry", "start_leader"),
                                  m, state)
    if not called:
        await m.answer("🧭 «Путь лидера» скоро будет доступен в этом сборке.")


@go_router.message(Command("casting"))
async def cmd_casting(m: Message, state: FSMContext):
    called = await _call_optional("app.routers.minicasting",
                                  ("open_minicasting", "show_minicasting", "mc_entry", "start_minicasting"),
                                  m, state)
    if not called:
        await m.answer("🎭 «Мини-кастинг» скоро будет доступен в этом сборке.")


@go_router.message(Command("apply"))
async def cmd_apply(m: Message, state: FSMContext):
    # передаём управление в apply, если есть
    called = await _call_optional("app.routers.apply",
                                  ("open_apply", "show_apply", "apply_entry", "start_apply"),
                                  m, state)
    if not called:
        await m.answer("📝 Заявка лидера временно недоступна.")


@go_router.message(Command("ping"))
async def cmd_ping(m: Message):
    await m.answer("pong 🟢")


@go_router.message(Command("healthz"))
async def cmd_healthz(m: Message):
    # для health-check Render
    await m.answer("ok")


@go_router.message(Command("cancel"))
async def cmd_cancel(m: Message, state: FSMContext):
    await state.clear()
    await m.answer("↩️ Сброс состояний. Возвращаю в меню.")
    await show_main_menu(m)


# ──────────────────────────────────────────────────────────────────────────────
# Callback-навигация (go:*)
# ──────────────────────────────────────────────────────────────────────────────
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
    # сначала пробуем модуль privacy
    called = await _call_optional("app.routers.privacy", ("show_privacy", "open_privacy"), cq)
    if not called:
        await show_privacy(cq)


@go_router.callback_query(F.data == "go:settings")
async def cb_go_settings(cq: CallbackQuery):
    await cq.answer()
    called = await _call_optional("app.routers.settings", ("show_settings", "open_settings"), cq)
    if not called:
        await show_settings(cq)


@go_router.callback_query(F.data == "go:progress")
async def cb_go_progress(cq: CallbackQuery):
    await cq.answer()
    if progress_entry:
        await progress_entry(cq.message)
        return
    called = await _call_optional("app.routers.progress", ("show_progress", "open_progress"), cq.message)
    if not called:
        await cq.message.answer("📈 Раздел «Мой прогресс» временно недоступен.")


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
        await cq.message.answer("🏋️ Раздел «Тренировка дня» временно недоступен.")


@go_router.callback_query(F.data == "go:leader")
async def cb_go_leader(cq: CallbackQuery, state: FSMContext):
    await cq.answer()
    called = await _call_optional("app.routers.leader",
                                  ("open_leader", "show_leader", "leader_entry", "start_leader"),
                                  cq.message, state)
    if not called:
        await cq.message.answer("🧭 «Путь лидера» скоро будет доступен в этом сборке.")


@go_router.callback_query(F.data == "go:casting")
async def cb_go_casting(cq: CallbackQuery, state: FSMContext):
    await cq.answer()
    called = await _call_optional("app.routers.minicasting",
                                  ("open_minicasting", "show_minicasting", "mc_entry", "start_minicasting"),
                                  cq.message, state)
    if not called:
        await cq.message.answer("🎭 «Мини-кастинг» скоро будет доступен в этом сборке.")


@go_router.callback_query(F.data == "go:extended")
async def cb_go_extended(cq: CallbackQuery):
    await cq.answer()
    called = await _call_optional("app.routers.extended",
                                  ("open_extended", "show_extended", "extended_entry"))
    if not called:
        await cq.message.answer("⭐️ «Расширенная версия» появится после стабилизации dev-сборки.")
