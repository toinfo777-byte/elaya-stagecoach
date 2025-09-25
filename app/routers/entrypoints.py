from __future__ import annotations
from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.keyboards.reply import (
    BTN_TRAINING, BTN_CASTING, BTN_APPLY, BTN_PROGRESS,
    BTN_HELP, BTN_SETTINGS, BTN_EXTENDED, BTN_MENU, main_menu_kb
)

router = Router(name="entrypoints")

@router.message(StateFilter("*"), F.text == BTN_TRAINING)
async def on_training(m: Message, state: FSMContext):
    await state.clear()
    try:
        from app.routers.training import training_start
        await training_start(m, state)
    except Exception:
        await m.answer("Раздел тренировки скоро вернётся. Открываю меню.", reply_markup=main_menu_kb())

@router.message(StateFilter("*"), F.text == BTN_CASTING)
async def on_minicasting(m: Message, state: FSMContext):
    await state.clear()
    try:
        from app.routers.minicasting import start_minicasting
        await start_minicasting(m, state)
    except Exception:
        await m.answer("Мини-кастинг временно недоступен. Открываю меню.", reply_markup=main_menu_kb())

@router.message(StateFilter("*"), F.text == BTN_APPLY)
async def on_leader(m: Message, state: FSMContext):
    await state.clear()
    try:
        from app.routers.leader import leader_entry
        await leader_entry(m, state)
    except Exception:
        await m.answer("Путь лидера временно недоступен. Открываю меню.", reply_markup=main_menu_kb())

@router.message(StateFilter("*"), F.text == BTN_PROGRESS)
async def on_progress(m: Message, state: FSMContext):
    await state.clear()
    try:
        from app.routers.progress import show_progress
        await show_progress(m)
    except Exception:
        await m.answer("📈 Мой прогресс\n\n• Стрик: 0\n• Этюдов за 7 дней: 0", reply_markup=main_menu_kb())

@router.message(StateFilter("*"), F.text == BTN_HELP)
async def on_help(m: Message, state: FSMContext):
    await state.clear()
    try:
        from app.routers.help import help_cmd
        await help_cmd(m, state)
    except Exception:
        await m.answer("Помощь недоступна. Открываю меню.", reply_markup=main_menu_kb())

@router.message(StateFilter("*"), F.text == BTN_SETTINGS)
async def on_settings(m: Message, state: FSMContext):
    await state.clear()
    try:
        from app.routers.settings import open_settings
        await open_settings(m, state)
    except Exception:
        await m.answer("Настройки недоступны. Открываю меню.", reply_markup=main_menu_kb())

@router.message(StateFilter("*"), F.text == BTN_EXTENDED)
async def on_extended(m: Message, state: FSMContext):
    await state.clear()
    try:
        from app.routers.extended import extended_pitch
        await extended_pitch(m)
    except Exception:
        await m.answer("⭐ Расширенная версия скоро. Открываю меню.", reply_markup=main_menu_kb())

@router.message(StateFilter("*"), F.text == BTN_MENU)
async def on_menu(m: Message, state: FSMContext):
    await state.clear()
    await m.answer("Готово! Открываю меню.", reply_markup=main_menu_kb())
