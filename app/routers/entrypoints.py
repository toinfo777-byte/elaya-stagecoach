from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

# экраны (меню/политика/настройки)
from app.routers.help import show_main_menu, show_privacy, show_settings

# разделы
from app.routers.training import show_training_levels
from app.routers.minicasting import start_minicasting
from app.routers.leader import leader_entry
from app.routers.progress import show_progress

go_router = Router(name="entrypoints")


# ---------- универсальные входы-команды (работают из ЛЮБОГО состояния) ----------
@go_router.message(StateFilter("*"), Command("menu"))
async def cmd_menu(m: Message, state: FSMContext):
    await state.clear()
    await show_main_menu(m)


@go_router.message(StateFilter("*"), Command("training"))
async def cmd_training(m: Message, state: FSMContext):
    await state.clear()
    await show_training_levels(m, state)


@go_router.message(StateFilter("*"), Command("casting"))
async def cmd_casting(m: Message, state: FSMContext):
    await state.clear()
    await start_minicasting(m, state)


@go_router.message(StateFilter("*"), Command("leader"))
@go_router.message(StateFilter("*"), Command("apply"))
async def cmd_leader(m: Message, state: FSMContext):
    await state.clear()
    await leader_entry(m, state)


@go_router.message(StateFilter("*"), Command("progress"))
async def cmd_progress(m: Message, state: FSMContext):
    await state.clear()
    await show_progress(m)


@go_router.message(StateFilter("*"), Command("settings"))
async def cmd_settings(m: Message, state: FSMContext):
    await state.clear()
    await show_settings(m)


@go_router.message(StateFilter("*"), Command("privacy"))
async def cmd_privacy(m: Message, state: FSMContext):
    await state.clear()
    await show_privacy(m)


# ---------- алиасы callback_data (кнопки из меню/помощи/старые payload’ы) ----------
MENU = {"go:menu", "menu", "to_menu", "home", "main_menu"}
TRAIN = {"go:training", "training", "training:start"}
CAST  = {"go:casting", "casting"}
LEAD  = {"go:leader", "leader", "go:apply"}
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
    await show_training_levels(cb.message, state)  # show_* ждёт Message


@go_router.callback_query(StateFilter("*"), F.data.in_(CAST))
async def cb_casting(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.clear()
    await start_minicasting(cb.message, state)


@go_router.callback_query(StateFilter("*"), F.data.in_(LEAD))
async def cb_leader(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.clear()
    await leader_entry(cb.message, state)


@go_router.callback_query(StateFilter("*"), F.data.in_(PROGR))
async def cb_progress(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.clear()
    await show_progress(cb.message)


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


# ---------- страховка: любой неизвестный коллбэк -> меню ----------
@go_router.callback_query()
async def cb_fallback(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.clear()
    await show_main_menu(cb)
