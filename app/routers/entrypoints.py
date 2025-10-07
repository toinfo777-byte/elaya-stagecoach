# app/routers/entrypoints.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

# экраны из help
from app.routers.help import show_main_menu, show_privacy, show_settings
# вход в тренировку и прогресс
from app.routers.training import show_training_levels as training_entry
from app.routers.progress import show_progress

go_router = Router(name="go_router")

# ── универсальные входы из инлайн-меню "go:*" ────────────────────────────────
@g o_router.callback_query(F.data == "go:menu")
async def go_menu(cq: CallbackQuery):
    await show_main_menu(cq)

@g o_router.callback_query(F.data == "go:training")
async def go_training(cq: CallbackQuery, state: FSMContext):
    await cq.answer()
    # show_training_levels ждёт Message + state
    await training_entry(cq.message, state)

@g o_router.callback_query(F.data == "go:progress")
async def go_progress(cq: CallbackQuery):
    await cq.answer()
    # show_progress ждёт Message
    await show_progress(cq.message)

@g o_router.callback_query(F.data == "go:privacy")
async def go_privacy(cq: CallbackQuery):
    await cq.answer()
    await show_privacy(cq)

@g o_router.callback_query(F.data == "go:settings")
async def go_settings(cq: CallbackQuery):
    await cq.answer()
    await show_settings(cq)

# (опционально) fallback на текстовые кнопки «В меню»
@g o_router.message(F.text.in_({"Меню", "В меню", "🏠 В меню"}))
async def txt_menu(msg: Message):
    await show_main_menu(msg)
