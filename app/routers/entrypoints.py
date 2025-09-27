from __future__ import annotations
from aiogram import Router, F
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from app.routers.help import show_main_menu, show_privacy, show_settings
from app.routers.training import show_training_levels
from app.routers.leader import leader_entry
from app.routers.minicasting import start_minicasting
from app.routers.progress import show_progress

go_router = Router(name="entrypoints")


async def _as_reply(obj: Message | CallbackQuery):
    return obj.message if isinstance(obj, CallbackQuery) else obj


# -------- СЛЭШ-КОМАНДЫ (из любого состояния) --------
@go_router.message(StateFilter("*"), CommandStart())
async def cmd_start(m: Message, state: FSMContext):
    await state.clear()
    payload = (m.text or "").split(maxsplit=1)
    arg = payload[1] if len(payload) > 1 else ""
    if arg.startswith("go_training"):
        return await show_training_levels(m)
    if arg.startswith("go_casting"):
        return await start_minicasting(m)
    return await show_main_menu(m)

@go_router.message(StateFilter("*"), Command("menu"))
async def cmd_menu(m: Message, state: FSMContext):
    await state.clear()
    await show_main_menu(m)

@go_router.message(StateFilter("*"), Command("cancel"))
async def cmd_cancel(m: Message, state: FSMContext):
    await state.clear()
    await m.answer("Сбросил текущее действие.")
    await show_main_menu(m)

@go_router.message(StateFilter("*"), Command("help"))
async def cmd_help(m: Message, state: FSMContext):
    await state.clear()
    await show_main_menu(m)

@go_router.message(StateFilter("*"), Command("training"))
async def cmd_training(m: Message, state: FSMContext):
    await state.clear()
    await show_training_levels(m)

@go_router.message(StateFilter("*"), Command("casting"))
async def cmd_casting(m: Message, state: FSMContext):
    await state.clear()
    await start_minicasting(m)

@go_router.message(StateFilter("*"), Command("leader"))
async def cmd_leader(m: Message, state: FSMContext):
    await state.clear()
    await leader_entry(m)

@go_router.message(StateFilter("*"), Command("progress"))
async def cmd_progress(m: Message, state: FSMContext):
    await state.clear()
    await show_progress(m)

@go_router.message(StateFilter("*"), Command("privacy"))
async def cmd_privacy(m: Message, state: FSMContext):
    await state.clear()
    await show_privacy(m)

@go_router.message(StateFilter("*"), Command("settings"))
async def cmd_settings(m: Message, state: FSMContext):
    await state.clear()
    await show_settings(m)


# -------- ТЕКСТОВЫЕ КНОПКИ ReplyKeyboard --------
@go_router.message(StateFilter("*"), F.text.in_({
    "🏋️ Тренировка дня", "🎭 Мини-кастинг", "🧭 Путь лидера",
    "📈 Мой прогресс", "🔐 Политика", "⚙️ Настройки",
    "💬 Помощь", "🏠 В меню", "Меню"
}))
async def on_reply_buttons(m: Message, state: FSMContext):
    await state.clear()
    text = (m.text or "").strip()
    if text.startswith("🏋️"):
        return await show_training_levels(m)
    if text.startswith("🎭"):
        return await start_minicasting(m)
    if text.startswith("🧭"):
        return await leader_entry(m)
    if text.startswith("📈"):
        return await show_progress(m)
    if text.startswith("🔐"):
        return await show_privacy(m)
    if text.startswith("⚙️"):
        return await show_settings(m)
    # «Помощь» и все «в меню» → главное меню
    await show_main_menu(m)


# -------- Алиасы для разных callback_data --------
MENU = {"go:menu", "menu", "to_menu", "home", "main_menu", "В_меню", "core:menu"}
TRAIN = {"go:training", "training", "training:start"}
LEAD  = {"go:leader", "leader"}
CAST  = {"go:casting", "casting"}
PROGR = {"go:progress", "progress"}
SETTS = {"go:settings", "settings"}
PRIV  = {"go:privacy", "privacy", "policy"}

@go_router.callback_query(StateFilter("*"), F.data.in_(MENU))
async def cb_menu(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.clear()
    await show_main_menu(cb)

@go_router.callback_query(StateFilter("*"), F.data.in_(TRAIN))
async def cb_training(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.clear()
    await show_training_levels(cb)

@go_router.callback_query(StateFilter("*"), F.data.in_(LEAD))
async def cb_leader(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.clear()
    await leader_entry(cb)

@go_router.callback_query(StateFilter("*"), F.data.in_(CAST))
async def cb_cast(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.clear()
    await start_minicasting(cb)

@go_router.callback_query(StateFilter("*"), F.data.in_(PROGR))
async def cb_progress(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.clear()
    await show_progress(cb)

@go_router.callback_query(StateFilter("*"), F.data.in_(SETTS))
async def cb_settings(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.clear()
    await show_settings(cb)

@go_router.callback_query(StateFilter("*"), F.data.in_(PRIV))
async def cb_privacy(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.clear()
    await show_privacy(cb)

# Фоллбек: любой неизвестный клик → в меню
@go_router.callback_query()
async def cb_fallback(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.clear()
    await show_main_menu(cb)
