# app/routers/training.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.keyboards.reply import main_menu_kb, BTN_TRAINING

router = Router(name="training")

class Training(StatesGroup):
    wait_done = State()

def training_levels_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="Уровень 1", callback_data="tr:l1")
    kb.button(text="Уровень 2", callback_data="tr:l2")
    kb.button(text="Уровень 3", callback_data="tr:l3")
    kb.button(text="✅ Выполнил(а)", callback_data="tr:done")
    kb.adjust(2, 2)
    return kb.as_markup()

async def _start_training_core(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "🏋️ Тренировка дня\n\nВыбери уровень. После выполнения нажми «✅ Выполнил(а)».",
        reply_markup=training_levels_kb()
    )
    await state.set_state(Training.wait_done)

# ← новое: совместимая точка входа, чтобы её мог импортировать start.py
async def training_start(message: Message, state: FSMContext):
    await _start_training_core(message, state)

@router.message(StateFilter("*"), F.text == BTN_TRAINING)
async def training_btn(message: Message, state: FSMContext):
    await _start_training_core(message, state)

@router.message(StateFilter("*"), Command("training"))
async def training_cmd(message: Message, state: FSMContext):
    await _start_training_core(message, state)

@router.callback_query(F.data.startswith("tr:"), Training.wait_done)
async def training_actions(call: CallbackQuery, state: FSMContext):
    payload = call.data.split(":", 1)[1]
    await call.answer()
    if payload == "done":
        await call.message.answer("🔥 Отлично! День засчитан. Увидимся завтра!")
        await state.clear()
        return await call.message.answer("Готово! Открываю меню.", reply_markup=main_menu_kb())
    # переключение уровней — просто подтверждаем
    await call.message.answer("Выбери «✅ Выполнил(а)», когда закончишь.")

# ← алиас для legacy-импорта: from app.routers.training import training_entry
training_entry = training_start
