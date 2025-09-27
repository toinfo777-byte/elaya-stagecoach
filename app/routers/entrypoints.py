from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

# твои реальные экран-функции:
from app.routers.help import show_main_menu, show_privacy, show_settings
from app.routers.training import show_training_levels
from app.routers.leader import leader_entry
from app.routers.minicasting import start_minicasting
from app.routers.progress import show_progress
# если заявка отдельно — раскомментируй:
# from app.routers.apply import start_apply

router = Router(name="entrypoints")


# ---------- команды (работают из ЛЮБОГО состояния) ----------
@router.message(StateFilter("*"), Command("menu"))
async def ep_cmd_menu(m: Message, state: FSMContext):
    await state.clear()
    await show_main_menu(m)

@router.message(StateFilter("*"), Command("training"))
async def ep_cmd_training(m: Message, state: FSMContext):
    await state.clear()
    await show_training_levels(m, state)

@router.message(StateFilter("*"), Command("apply"))
@router.message(StateFilter("*"), Command("leader"))
async def ep_cmd_leader(m: Message, state: FSMContext):
    await state.clear()
    await leader_entry(m, state)

@router.message(StateFilter("*"), Command("casting"))
async def ep_cmd_casting(m: Message, state: FSMContext):
    await state.clear()
    await start_minicasting(m, state)

@router.message(StateFilter("*"), Command("progress"))
async def ep_cmd_progress(m: Message, state: FSMContext):
    await state.clear()
    await show_progress(m)

@router.message(StateFilter("*"), Command("settings"))
async def ep_cmd_settings(m: Message, state: FSMContext):
    await state.clear()
    await show_settings(m, state)

@router.message(StateFilter("*"), Command("privacy"))
async def ep_cmd_privacy(m: Message, state: FSMContext):
    await state.clear()
    await show_privacy(m)

# если нужен /apply из отдельного модуля:
# @router.message(StateFilter("*"), Command("apply"))
# async def ep_cmd_apply(m: Message, state: FSMContext):
#     await state.clear()
#     await start_apply(m, state)


# ---------- алиасы callback_data для разных кнопок ----------
MENU = {"go:menu", "menu", "to_menu", "core:menu", "home", "main_menu", "В_меню"}
TRAIN = {"go:training", "training", "training:start"}
LEAD  = {"go:leader", "go:apply", "leader", "apply"}
CAST  = {"go:casting", "casting"}
PROGR = {"go:progress", "progress"}
SETTS = {"go:settings", "settings"}
PRIV  = {"go:privacy", "privacy", "policy"}

@router.callback_query(StateFilter("*"), F.data.in_(MENU))
async def ep_cb_menu(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.clear()
    await show_main_menu(cb.message)

@router.callback_query(StateFilter("*"), F.data.in_(TRAIN))
async def ep_cb_training(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.clear()
    await show_training_levels(cb.message, state)

@router.callback_query(StateFilter("*"), F.data.in_(LEAD))
async def ep_cb_leader(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.clear()
    await leader_entry(cb.message, state)

@router.callback_query(StateFilter("*"), F.data.in_(CAST))
async def ep_cb_casting(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.clear()
    await start_minicasting(cb.message, state)

@router.callback_query(StateFilter("*"), F.data.in_(PROGR))
async def ep_cb_progress(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.clear()
    await show_progress(cb.message)

@router.callback_query(StateFilter("*"), F.data.in_(SETTS))
async def ep_cb_settings(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.clear()
    await show_settings(cb.message, state)

@router.callback_query(StateFilter("*"), F.data.in_(PRIV))
async def ep_cb_privacy(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.clear()
    await show_privacy(cb.message)


# ---------- текстовые кнопки ReplyKeyboard (если используешь «большое меню») ----------
@router.message(StateFilter("*"), F.text.in_({"🏠 В меню", "Меню", "В меню"}))
async def ep_txt_menu(m: Message, state: FSMContext):
    await state.clear()
    await show_main_menu(m)

@router.message(StateFilter("*"), F.text == "🏋️ Тренировка дня")
async def ep_txt_training(m: Message, state: FSMContext):
    await state.clear()
    await show_training_levels(m, state)

@router.message(StateFilter("*"), F.text == "🎭 Мини-кастинг")
async def ep_txt_casting(m: Message, state: FSMContext):
    await state.clear()
    await start_minicasting(m, state)

@router.message(StateFilter("*"), F.text == "🧭 Путь лидера")
async def ep_txt_leader(m: Message, state: FSMContext):
    await state.clear()
    await leader_entry(m, state)

@router.message(StateFilter("*"), F.text == "📈 Мой прогресс")
async def ep_txt_progress(m: Message, state: FSMContext):
    await state.clear()
    await show_progress(m)

@router.message(StateFilter("*"), F.text == "⚙️ Настройки")
async def ep_txt_settings(m: Message, state: FSMContext):
    await state.clear()
    await show_settings(m, state)

@router.message(StateFilter("*"), F.text == "🔐 Политика")
async def ep_txt_privacy(m: Message, state: FSMContext):
    await state.clear()
    await show_privacy(m)


__all__ = ["router"]
