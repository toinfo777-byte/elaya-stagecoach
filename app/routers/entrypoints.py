# app/routers/entrypoints.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.routers.help import show_main_menu, show_privacy, show_settings
from app.routers.training import show_training_levels
from app.routers.progress import show_progress

router = Router(name="entrypoints")  # основной роутер модуля

# Срабатывает из любого состояния
@router.message(StateFilter("*"), F.text.in_({"💬 Помощь", "Меню", "🏠 Меню", "🏠 В меню"}))
async def ep_help(msg: Message, state: FSMContext):
    await state.clear()
    await show_main_menu(msg)

@router.message(StateFilter("*"), F.text == "🏋️ Тренировка дня")
async def ep_training(msg: Message, state: FSMContext):
    await state.clear()
    await show_training_levels(msg)

@router.message(StateFilter("*"), F.text == "🎭 Мини-кастинг")
async def ep_casting(msg: Message, state: FSMContext):
    await state.clear()
    from app.routers.minicasting import start_minicasting
    await start_minicasting(msg)

@router.message(StateFilter("*"), F.text == "🧭 Путь лидера")
async def ep_leader(msg: Message, state: FSMContext):
    await state.clear()
    from app.routers.leader import leader_entry
    await leader_entry(msg)

@router.message(StateFilter("*"), F.text == "📈 Мой прогресс")
async def ep_progress(msg: Message, state: FSMContext):
    await state.clear()
    await show_progress(msg)

@router.message(StateFilter("*"), F.text == "🔐 Политика")
async def ep_privacy(msg: Message, state: FSMContext):
    await state.clear()
    await show_privacy(msg)

@router.message(StateFilter("*"), F.text == "⚙️ Настройки")
async def ep_settings(msg: Message, state: FSMContext):
    await state.clear()
    await show_settings(msg)

# --- ВАЖНО: экспорт под именем, которое ждёт main.py ---
go_router = router
__all__ = ["go_router"]
