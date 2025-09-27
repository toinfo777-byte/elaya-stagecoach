# app/routers/entrypoints.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command, StateFilter, CommandStart
from aiogram.filters.command import CommandObject
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

go_router = Router(name="entrypoints")


# ---------- helpers ----------
def _as_message(obj: Message | CallbackQuery) -> Message:
    return obj.message if isinstance(obj, CallbackQuery) else obj


async def _to_menu(obj: Message | CallbackQuery, state: FSMContext) -> None:
    """Глобальный вход в меню: чистим стейт и показываем главное меню."""
    # ленивый импорт, чтобы не ронять модуль, если help.py меняется
    from app.routers.help import show_main_menu
    await state.clear()
    await show_main_menu(obj)


# ---------- /start (в т.ч. deep-link) ----------
@go_router.message(StateFilter("*"), CommandStart())
async def cmd_start(m: Message, command: CommandObject, state: FSMContext):
    arg = (command.args or "").strip().lower()
    if arg.startswith("go_training"):
        from app.routers.training import show_training_levels
        await state.clear()
        return await show_training_levels(m, state)
    if arg.startswith("go_casting"):
        from app.routers.minicasting import start_minicasting
        await state.clear()
        return await start_minicasting(m, state)
    # дефолт — в меню
    return await _to_menu(m, state)


# ---------- СЛЭШ-КОМАНДЫ (работают в ЛЮБОМ состоянии) ----------
@go_router.message(StateFilter("*"), Command("menu"))
async def cmd_menu(m: Message, state: FSMContext):
    await _to_menu(m, state)


@go_router.message(StateFilter("*"), Command("training"))
async def cmd_training(m: Message, state: FSMContext):
    from app.routers.training import show_training_levels
    await state.clear()
    await show_training_levels(m, state)


@go_router.message(StateFilter("*"), Command("leader"))
@go_router.message(StateFilter("*"), Command("apply"))  # алиас, если используете /apply
async def cmd_leader(m: Message, state: FSMContext):
    from app.routers.leader import leader_entry
    await state.clear()
    await leader_entry(m, state)


@go_router.message(StateFilter("*"), Command("casting"))
async def cmd_casting(m: Message, state: FSMContext):
    from app.routers.minicasting import start_minicasting
    await state.clear()
    await start_minicasting(m, state)


@go_router.message(StateFilter("*"), Command("progress"))
async def cmd_progress(m: Message, state: FSMContext):
    from app.routers.progress import show_progress
    await state.clear()
    await show_progress(m)


@go_router.message(StateFilter("*"), Command("settings"))
async def cmd_settings(m: Message, state: FSMContext):
    from app.routers.help import show_settings
    await state.clear()
    await show_settings(m)


@go_router.message(StateFilter("*"), Command("privacy"))
async def cmd_privacy(m: Message, state: FSMContext):
    from app.routers.help import show_privacy
    await state.clear()
    await show_privacy(m)


# ---------- ТЕКСТОВЫЕ кнопки из ReplyKeyboard (нижнее «большое меню») ----------
@go_router.message(StateFilter("*"), F.text.in_({"🏠 Меню", "Меню", "В меню"}))
async def text_menu(m: Message, state: FSMContext):
    await _to_menu(m, state)


@go_router.message(StateFilter("*"), F.text == "🏋️ Тренировка дня")
async def text_training(m: Message, state: FSMContext):
    from app.routers.training import show_training_levels
    await state.clear()
    await show_training_levels(m, state)


@go_router.message(StateFilter("*"), F.text == "🎭 Мини-кастинг")
async def text_casting(m: Message, state: FSMContext):
    from app.routers.minicasting import start_minicasting
    await state.clear()
    await start_minicasting(m, state)


@go_router.message(StateFilter("*"), F.text == "🧭 Путь лидера")
async def text_leader(m: Message, state: FSMContext):
    from app.routers.leader import leader_entry
    await state.clear()
    await leader_entry(m, state)


@go_router.message(StateFilter("*"), F.text == "📈 Мой прогресс")
async def text_progress(m: Message, state: FSMContext):
    from app.routers.progress import show_progress
    await state.clear()
    await show_progress(m)


# ---------- КОЛЛБЭКИ (инлайн-кнопки): алиасы старых/разных payload’ов ----------
MENU = {"go:menu", "menu", "В_меню", "to_menu", "home", "main_menu", "core:menu"}
TRAIN = {"go:training", "training", "training:start", "tr:entry"}
LEAD  = {"go:leader", "leader", "go:apply"}
CAST  = {"go:casting", "casting", "mc:entry"}
PROGR = {"go:progress", "progress"}
SETTS = {"go:settings", "settings"}
PRIV  = {"go:privacy", "privacy", "policy"}

@go_router.callback_query(StateFilter("*"), F.data.in_(MENU))
async def cb_menu(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await _to_menu(cb, state)


@go_router.callback_query(StateFilter("*"), F.data.in_(TRAIN))
async def cb_train(cb: CallbackQuery, state: FSMContext):
    from app.routers.training import show_training_levels
    await cb.answer()
    await state.clear()
    await show_training_levels(_as_message(cb), state)


@go_router.callback_query(StateFilter("*"), F.data.in_(LEAD))
async def cb_lead(cb: CallbackQuery, state: FSMContext):
    from app.routers.leader import leader_entry
    await cb.answer()
    await state.clear()
    await leader_entry(cb, state)


@go_router.callback_query(StateFilter("*"), F.data.in_(CAST))
async def cb_cast(cb: CallbackQuery, state: FSMContext):
    from app.routers.minicasting import start_minicasting
    await cb.answer()
    await state.clear()
    await start_minicasting(cb, state)


@go_router.callback_query(StateFilter("*"), F.data.in_(PROGR))
async def cb_prog(cb: CallbackQuery, state: FSMContext):
    from app.routers.progress import show_progress
    await cb.answer()
    await state.clear()
    await show_progress(cb)


@go_router.callback_query(StateFilter("*"), F.data.in_(SETTS))
async def cb_set(cb: CallbackQuery, state: FSMContext):
    from app.routers.help import show_settings
    await cb.answer()
    await state.clear()
    await show_settings(cb)


@go_router.callback_query(StateFilter("*"), F.data.in_(PRIV))
async def cb_priv(cb: CallbackQuery, state: FSMContext):
    from app.routers.help import show_privacy
    await cb.answer()
    await state.clear()
    await show_privacy(cb)


# ---------- ФОЛЛБЕК: любой неизвестный клик -> меню ----------
@go_router.callback_query()
async def cb_fallback(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await _to_menu(cb, state)


__all__ = ["go_router"]
