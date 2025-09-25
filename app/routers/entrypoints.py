# app/routers/entrypoints.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.keyboards.reply import (
    BTN_TRAINING, BTN_CASTING, BTN_APPLY, BTN_PROGRESS,
    BTN_HELP, BTN_SETTINGS, BTN_EXTENDED, BTN_MENU
)
from app.keyboards.reply import main_menu_kb

# вызовы в соответствующие роутеры
from app.routers.minicasting import start_minicasting
from app.routers.leader import start_leader_btn
from app.routers.training import show_training_levels

router = Router(name="entrypoints")

@router.message(StateFilter("*"), F.text == BTN_TRAINING)
async def ep_training(msg: Message, state: FSMContext):
    await state.clear()
    await show_training_levels(msg)

@router.message(StateFilter("*"), F.text == BTN_CASTING)
async def ep_casting(msg: Message, state: FSMContext):
    await state.clear()
    await start_minicasting(msg, state)

@router.message(StateFilter("*"), F.text == BTN_APPLY)
async def ep_leader(msg: Message, state: FSMContext):
    await state.clear()
    await start_leader_btn(msg, state)

@router.message(StateFilter("*"), F.text == BTN_PROGRESS)
async def ep_progress(msg: Message, state: FSMContext):
    await state.clear()
    # простой статический ответ; если есть свой show_progress — дерни его
    await msg.answer(
        "📈 Мой прогресс\n\n• Стрик: 0\n• Этюдов за 7 дней: 0\n\n"
        "Продолжай каждый день — «Тренировка дня» в один клик 👇",
        reply_markup=main_menu_kb()
    )

@router.message(StateFilter("*"), F.text == BTN_HELP)
async def ep_help(msg: Message, state: FSMContext):
    await state.clear()
    from app.routers.help import help_cmd  # локальный импорт, чтобы не ловить циклы
    await help_cmd(msg, state)

@router.message(StateFilter("*"), F.text == BTN_SETTINGS)
async def ep_settings(msg: Message, state: FSMContext):
    await state.clear()
    from app.routers.settings import open_settings
    await open_settings(msg, state)

@router.message(StateFilter("*"), F.text == BTN_EXTENDED)
async def ep_extended(msg: Message, state: FSMContext):
    await state.clear()
    try:
        from app.routers.extended import extended_pitch
        await extended_pitch(msg)
    except Exception:
        await msg.answer("⭐ Расширенная версия скоро. Возвращаю в меню.", reply_markup=main_menu_kb())

@router.message(StateFilter("*"), F.text == BTN_MENU)
async def ep_menu(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer("Готово! Открываю меню.", reply_markup=main_menu_kb())
