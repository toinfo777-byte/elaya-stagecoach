# app/routers/training.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.keyboards.reply import main_menu_kb, BTN_TRAINING

router = Router(name="training")

# ——— UI ———

def kb_training_levels():
    kb = InlineKeyboardBuilder()
    kb.button(text="Уровень 1 · 5 мин", callback_data="tr:l1")
    kb.button(text="Уровень 2 · 10 мин", callback_data="tr:l2")
    kb.button(text="Уровень 3 · 15 мин", callback_data="tr:l3")
    kb.button(text="✅ Выполнил(а)",    callback_data="tr:done")
    kb.button(text="🏠 В меню",         callback_data="go:menu")
    kb.adjust(1, 1, 1, 1, 1)
    return kb.as_markup()

TRAINING_PLANS = {
    "l1": (
        "Разогрев · 5 минут\n"
        "1) Дыхание — 1 мин\n"
        "2) Рот/язык/щелчки — 2 мин\n"
        "3) Артикуляция — 2 мин\n\n"
        "💡 Совет: запиши 15 сек «до/после»."
    ),
    "l2": (
        "База · 10 минут\n"
        "1) Паузы и атака фразы — 3 мин\n"
        "2) Тембр — 3 мин\n"
        "3) Дикция (скороговорки) — 4 мин"
    ),
    "l3": (
        "Про · 15 минут\n"
        "1) Резонаторы — 5 мин\n"
        "2) Текст с паузами — 5 мин\n"
        "3) Микро-этюд — 5 мин"
    ),
}

# ——— Entry points ———

async def training_start(msg: Message, state: FSMContext | None = None) -> None:
    """Универсальный старт тренировки (команды, кнопки, диплинки)."""
    if state is not None:
        await state.clear()
    await msg.answer(
        "🏋️ Тренировка дня\n\nВыбери уровень. После выполнения нажми «✅ Выполнил(а)».",
        reply_markup=kb_training_levels(),
    )

# ✅ алиас для совместимости со старыми импортами
training_entry = training_start

# Команда /training — из любого состояния
@router.message(StateFilter("*"), Command("training"))
async def cmd_training(msg: Message, state: FSMContext):
    await training_start(msg, state)

# Кнопка из ReplyKeyboard («🏋️ Тренировка дня»)
@router.message(StateFilter("*"), F.text == BTN_TRAINING)
async def btn_training(msg: Message, state: FSMContext):
    await training_start(msg, state)

# Переход из инлайн-меню (help / go-кнопки)
@router.callback_query(StateFilter("*"), F.data == "go:training")
async def go_training(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await training_start(cb.message, state)

# ——— Callbacks ———

@router.callback_query(F.data.in_({"tr:l1", "tr:l2", "tr:l3"}))
async def show_plan(cb: CallbackQuery):
    await cb.answer()
    key = cb.data.split(":")[1]
    await cb.message.answer(TRAINING_PLANS[key])

@router.callback_query(F.data == "tr:done")
async def training_done(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    # здесь можно инкрементировать прогресс/стрик
    await cb.message.answer("🔥 Отлично! День засчитан. Увидимся завтра!")
    await state.clear()
    await cb.message.answer("Готово! Открываю меню.", reply_markup=main_menu_kb())
