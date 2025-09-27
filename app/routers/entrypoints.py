from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from app.routers.help import show_main_menu, show_help, show_privacy, show_settings
from app.routers.training import show_training_levels
from app.routers.minicasting import start_minicasting
from app.routers.progress import show_progress
from app.routers.leader import leader_entry  # убедись, что функция есть

router = Router(name="entrypoints")

# --- команды из любого состояния ---
@router.message(StateFilter("*"), Command("menu"))
async def ep_menu(m: Message, state: FSMContext):
    await state.clear()
    await show_main_menu(m)

@router.message(StateFilter("*"), Command("help"))
async def ep_help(m: Message, state: FSMContext):
    await state.clear()
    await show_help(m)

@router.message(StateFilter("*"), Command("training"))
async def ep_training(m: Message, state: FSMContext):
    await state.clear()
    await show_training_levels(m, state)

@router.message(StateFilter("*"), Command("casting"))
async def ep_casting(m: Message, state: FSMContext):
    await state.clear()
    await start_minicasting(m, state)

@router.message(StateFilter("*"), Command("leader"))
@router.message(StateFilter("*"), Command("apply"))
async def ep_leader(m: Message, state: FSMContext):
    await state.clear()
    await leader_entry(m)

@router.message(StateFilter("*"), Command("progress"))
async def ep_progress(m: Message, state: FSMContext):
    await state.clear()
    await show_progress(m)

@router.message(StateFilter("*"), Command("settings"))
async def ep_settings(m: Message, state: FSMContext):
    await state.clear()
    await show_settings(m)

@router.message(StateFilter("*"), Command("privacy"))
async def ep_privacy(m: Message, state: FSMContext):
    await state.clear()
    await show_privacy(m)

# --- алиасы для инлайн-кнопок (включая go:help) ---
@router.callback_query(StateFilter("*"), F.data == "go:menu")
async def cb_menu(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await show_main_menu(cb)

@router.callback_query(StateFilter("*"), F.data == "go:help")
async def cb_help(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await show_help(cb)
