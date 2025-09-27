# app/routers/entrypoints.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

go = Router(name="entrypoints")


# -------- внутренняя утилита: безопасно импортируем и вызываем целевую функцию --------
async def _call_entry(mod_path: str, func_name: str, event: Message | CallbackQuery, state: FSMContext | None = None):
    """
    Ленивая загрузка и вызов entry-функции.
    Пытается вызвать с (event, state) -> (event) -> (event.message, state) -> (event.message).
    При ошибке — показывает главное меню.
    """
    try:
        module = __import__(mod_path, fromlist=[func_name])
        func = getattr(module, func_name)
    except Exception:
        # fallback в меню
        await _show_menu_fallback(event)
        return

    # пробуем разные сигнатуры, чтобы не падать из-за несовпадений
    try:
        return await func(event, state) if state is not None else await func(event)
    except TypeError:
        # возможно функция ждёт только Message/CallbackQuery без state
        try:
            return await func(event)
        except TypeError:
            # возможно функция ожидала Message вместо CallbackQuery
            msg = event.message if isinstance(event, CallbackQuery) else event
            try:
                return await func(msg, state) if state is not None else await func(msg)
            except Exception:
                await _show_menu_fallback(event)
                return
    except Exception:
        await _show_menu_fallback(event)
        return


async def _show_menu_fallback(event: Message | CallbackQuery):
    """Показываем главное меню как запасной вариант."""
    try:
        module = __import__("app.routers.help", fromlist=["show_main_menu"])
        show_main_menu = getattr(module, "show_main_menu")
    except Exception:
        return
    msg = event.message if isinstance(event, CallbackQuery) else event
    await show_main_menu(msg)


# ===================== Команды (сообщения) — работают из любого состояния =====================

@go.message(StateFilter("*"), Command("menu"))
async def ep_cmd_menu(m: Message, state: FSMContext):
    await state.clear()
    await _call_entry("app.routers.help", "show_main_menu", m)

@go.message(StateFilter("*"), Command("training"))
async def ep_cmd_training(m: Message, state: FSMContext):
    await state.clear()
    await _call_entry("app.routers.training", "show_training_levels", m, state)

@go.message(StateFilter("*"), Command("leader"))
@go.message(StateFilter("*"), Command("apply"))
async def ep_cmd_leader(m: Message, state: FSMContext):
    await state.clear()
    # если нет leader_entry, можно держать отдельный start_apply — _call_entry сам подстрахует
    await _call_entry("app.routers.leader", "leader_entry", m, state)

@go.message(StateFilter("*"), Command("casting"))
async def ep_cmd_casting(m: Message, state: FSMContext):
    await state.clear()
    await _call_entry("app.routers.minicasting", "start_minicasting", m, state)

@go.message(StateFilter("*"), Command("progress"))
async def ep_cmd_progress(m: Message, state: FSMContext):
    await state.clear()
    await _call_entry("app.routers.progress", "show_progress", m)

@go.message(StateFilter("*"), Command("settings"))
async def ep_cmd_settings(m: Message, state: FSMContext):
    await state.clear()
    await _call_entry("app.routers.help", "show_settings", m, state)

@go.message(StateFilter("*"), Command("privacy"))
async def ep_cmd_privacy(m: Message, state: FSMContext):
    await state.clear()
    await _call_entry("app.routers.help", "show_privacy", m)

@go.message(StateFilter("*"), Command("help"))
async def ep_cmd_help(m: Message, state: FSMContext):
    # передадим в существующий /help из вашего help.py
    await _call_entry("app.routers.help", "help_cmd", m, state)


# ===================== Коллбэки (инлайн-кнопки) — алиасы под разные payload’ы =====================

MENU    = {"go:menu", "menu", "to_menu", "core:menu", "home", "main_menu", "В_меню"}
TRAIN   = {"go:training", "training", "training:start"}
LEADER  = {"go:leader", "go:apply", "leader"}
CAST    = {"go:casting", "casting"}
PROGR   = {"go:progress", "progress"}
SETTS   = {"go:settings", "settings"}
PRIV    = {"go:privacy", "privacy", "policy"}

@go.callback_query(StateFilter("*"), F.data.in_(MENU))
async def ep_cb_menu(cq: CallbackQuery, state: FSMContext):
    await cq.answer()
    await state.clear()
    await _call_entry("app.routers.help", "show_main_menu", cq)

@go.callback_query(StateFilter("*"), F.data.in_(TRAIN))
async def ep_cb_training(cq: CallbackQuery, state: FSMContext):
    await cq.answer()
    await state.clear()
    await _call_entry("app.routers.training", "show_training_levels", cq, state)

@go.callback_query(StateFilter("*"), F.data.in_(LEADER))
async def ep_cb_leader(cq: CallbackQuery, state: FSMContext):
    await cq.answer()
    await state.clear()
    await _call_entry("app.routers.leader", "leader_entry", cq, state)

@go.callback_query(StateFilter("*"), F.data.in_(CAST))
async def ep_cb_casting(cq: CallbackQuery, state: FSMContext):
    await cq.answer()
    await state.clear()
    await _call_entry("app.routers.minicasting", "start_minicasting", cq, state)

@go.callback_query(StateFilter("*"), F.data.in_(PROGR))
async def ep_cb_progress(cq: CallbackQuery, state: FSMContext):
    await cq.answer()
    await state.clear()
    await _call_entry("app.routers.progress", "show_progress", cq)

@go.callback_query(StateFilter("*"), F.data.in_(SETTS))
async def ep_cb_settings(cq: CallbackQuery, state: FSMContext):
    await cq.answer()
    await state.clear()
    await _call_entry("app.routers.help", "show_settings", cq, state)

@go.callback_query(StateFilter("*"), F.data.in_(PRIV))
async def ep_cb_privacy(cq: CallbackQuery, state: FSMContext):
    await cq.answer()
    await state.clear()
    await _call_entry("app.routers.help", "show_privacy", cq)


# ============== Текстовые кнопки с ReplyKeyboard (если используете «большое меню») ==============

TEXT_MENU     = {"🏠 В меню", "Меню", "В меню"}
TEXT_TRAIN    = {"🏋️ Тренировка дня"}
TEXT_CAST     = {"🎭 Мини-кастинг"}
TEXT_LEADER   = {"🧭 Путь лидера"}
TEXT_PROGRESS = {"📈 Мой прогресс"}
TEXT_SETTINGS = {"⚙️ Настройки"}
TEXT_PRIVACY  = {"🔐 Политика"}

@go.message(StateFilter("*"), F.text.in_(TEXT_MENU))
async def ep_txt_menu(m: Message, state: FSMContext):
    await state.clear()
    await _call_entry("app.routers.help", "show_main_menu", m)

@go.message(StateFilter("*"), F.text.in_(TEXT_TRAIN))
async def ep_txt_training(m: Message, state: FSMContext):
    await state.clear()
    await _call_entry("app.routers.training", "show_training_levels", m, state)

@go.message(StateFilter("*"), F.text.in_(TEXT_CAST))
async def ep_txt_casting(m: Message, state: FSMContext):
    await state.clear()
    await _call_entry("app.routers.minicasting", "start_minicasting", m, state)

@go.message(StateFilter("*"), F.text.in_(TEXT_LEADER))
async def ep_txt_leader(m: Message, state: FSMContext):
    await state.clear()
    await _call_entry("app.routers.leader", "leader_entry", m, state)

@go.message(StateFilter("*"), F.text.in_(TEXT_PROGRESS))
async def ep_txt_progress(m: Message, state: FSMContext):
    await state.clear()
    await _call_entry("app.routers.progress", "show_progress", m)

@go.message(StateFilter("*"), F.text.in_(TEXT_SETTINGS))
async def ep_txt_settings(m: Message, state: FSMContext):
    await state.clear()
    await _call_entry("app.routers.help", "show_settings", m, state)

@go.message(StateFilter("*"), F.text.in_(TEXT_PRIVACY))
async def ep_txt_privacy(m: Message, state: FSMContext):
    await state.clear()
    await _call_entry("app.routers.help", "show_privacy", m)


# ============== Последний «страховочный» колбэк: любые неизвестные кнопки — в меню ==============

@go.callback_query()
async def ep_fallback_cb(cq: CallbackQuery):
    await cq.answer()
    await _show_menu_fallback(cq)


# совместимость с импортом r_entrypoints.router
router = go
__all__ = ["go", "router"]
