# app/routers/entrypoints.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

go_router = Router(name="go")


# ---------- helpers
async def _safe_import_call(mod_path: str, func_name: str, *args, **kwargs):
    """
    Ленивая загрузка функции-энтипоинта, чтобы избежать циклических импортов.
    Если функция недоступна — отправляем пользователю короткий фолбэк.
    """
    try:
        module = __import__(mod_path, fromlist=[func_name])
        func = getattr(module, func_name)
        return await func(*args, **kwargs)
    except Exception as e:
        # Фолбэк: тихо сообщаем и возвращаемся в меню
        target = args[0]  # Message или CallbackQuery.message
        msg = target if isinstance(target, Message) else target.message
        await msg.answer("Раздел временно недоступен. Возвращаю в меню.")
        # попытка открыть меню
        try:
            module = __import__("app.routers.help", fromlist=["show_main_menu"])
            show_main_menu = getattr(module, "show_main_menu")
            return await show_main_menu(msg)
        except Exception:
            return


# =============== Команды (сообщения) ===============

@go_router.message(StateFilter("*"), Command("menu"))
async def ep_menu_cmd(m: Message, state: FSMContext):
    await state.clear()
    await _safe_import_call("app.routers.help", "show_main_menu", m)


@go_router.message(StateFilter("*"), Command("training"))
async def ep_training_cmd(m: Message, state: FSMContext):
    await state.clear()
    await _safe_import_call("app.routers.training", "show_training_levels", m, state)


@go_router.message(StateFilter("*"), Command("leader"))
@go_router.message(StateFilter("*"), Command("apply"))
async def ep_leader_cmd(m: Message, state: FSMContext):
    await state.clear()
    await _safe_import_call("app.routers.leader", "leader_entry", m, state)


@go_router.message(StateFilter("*"), Command("casting"))
async def ep_casting_cmd(m: Message, state: FSMContext):
    await state.clear()
    await _safe_import_call("app.routers.minicasting", "start_minicasting", m, state)


@go_router.message(StateFilter("*"), Command("progress"))
async def ep_progress_cmd(m: Message, state: FSMContext):
    await state.clear()
    await _safe_import_call("app.routers.progress", "show_progress", m)


@go_router.message(StateFilter("*"), Command("privacy"))
async def ep_privacy_cmd(m: Message, state: FSMContext):
    await state.clear()
    await _safe_import_call("app.routers.help", "show_privacy", m)


@go_router.message(StateFilter("*"), Command("settings"))
async def ep_settings_cmd(m: Message, state: FSMContext):
    await state.clear()
    await _safe_import_call("app.routers.help", "show_settings", m, state)


# =============== Коллбэки (кнопки go:*) ===============

@go_router.callback_query(StateFilter("*"), F.data == "go:menu")
async def ep_menu_cb(cq: CallbackQuery, state: FSMContext):
    await cq.answer()
    await state.clear()
    await _safe_import_call("app.routers.help", "show_main_menu", cq.message)


@go_router.callback_query(StateFilter("*"), F.data == "go:training")
async def ep_training_cb(cq: CallbackQuery, state: FSMContext):
    await cq.answer()
    await state.clear()
    await _safe_import_call("app.routers.training", "show_training_levels", cq.message, state)


@go_router.callback_query(StateFilter("*"), F.data == "go:leader")
@go_router.callback_query(StateFilter("*"), F.data == "go:apply")
async def ep_leader_cb(cq: CallbackQuery, state: FSMContext):
    await cq.answer()
    await state.clear()
    await _safe_import_call("app.routers.leader", "leader_entry", cq, state)


@go_router.callback_query(StateFilter("*"), F.data == "go:casting")
async def ep_casting_cb(cq: CallbackQuery, state: FSMContext):
    await cq.answer()
    await state.clear()
    await _safe_import_call("app.routers.minicasting", "start_minicasting", cq, state)


@go_router.callback_query(StateFilter("*"), F.data == "go:progress")
async def ep_progress_cb(cq: CallbackQuery, state: FSMContext):
    await cq.answer()
    await state.clear()
    await _safe_import_call("app.routers.progress", "show_progress", cq.message)


@go_router.callback_query(StateFilter("*"), F.data == "go:privacy")
async def ep_privacy_cb(cq: CallbackQuery, state: FSMContext):
    await cq.answer()
    await state.clear()
    await _safe_import_call("app.routers.help", "show_privacy", cq.message)


@go_router.callback_query(StateFilter("*"), F.data == "go:settings")
async def ep_settings_cb(cq: CallbackQuery, state: FSMContext):
    await cq.answer()
    await state.clear()
    await _safe_import_call("app.routers.help", "show_settings", cq.message, state)


# Совместимость: можно импортировать как go_router, так и router
router = go_router
__all__ = ["go_router", "router"]
