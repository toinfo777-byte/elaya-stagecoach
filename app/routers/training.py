# app/routers/training.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.keyboards.reply import main_menu_kb

router = Router(name="training")

def training_levels_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="Уровень 1", callback_data="tr:l1")
    kb.button(text="Уровень 2", callback_data="tr:l2")
    kb.button(text="Уровень 3", callback_data="tr:l3")
    kb.button(text="✅ Выполнил(а)", callback_data="tr:done")
    kb.button(text="🏠 В меню", callback_data="go:menu")
    kb.adjust(3, 2)
    return kb.as_markup()

TRAINING = {
    "l1": (
        "Разогрев · ~5 мин\n"
        "1) Дыхание — 1 мин\n"
        "2) Рот–язык–щелчки — 2 мин\n"
        "3) Артикуляция — 2 мин\n\n"
        "💡 Совет: запиши 15 сек до/после."
    ),
    "l2": (
        "База · ~10 мин\n"
        "1) Паузы и атака — 3 мин\n"
        "2) Тембр — 3 мин\n"
        "3) Дикция (скороговорки) — 4 мин"
    ),
    "l3": (
        "Про · ~15 мин\n"
        "1) Резонаторы — 5 мин\n"
        "2) Текст с паузами — 5 мин\n"
        "3) Микро-этюд — 5 мин"
    ),
}

async def show_training_levels(msg: Message):
    await msg.answer(
        "🏋️ Тренировка дня\n\n"
        "Выбери уровень. После выполнения нажми «✅ Выполнил(а)».",
        reply_markup=training_levels_kb()
    )

@router.message(StateFilter("*"), Command("training"))
async def training_start(message: Message):
    await show_training_levels(message)

# алиас для совместимости со старыми импортами
training_entry = training_start

@router.callback_query(F.data == "go:training")
async def training_from_help(cb: CallbackQuery):
    await cb.answer()
    await cb.message.edit_reply_markup()
    await show_training_levels(cb.message)

@router.callback_query(F.data.in_({"tr:l1", "tr:l2", "tr:l3"}))
async def training_show_plan(cb: CallbackQuery):
    await cb.answer()
    key = cb.data.split(":")[1]
    await cb.message.answer(TRAINING[key])

@router.callback_query(F.data == "tr:done")
async def training_done(cb: CallbackQuery):
    await cb.answer("Засчитано!")
    await cb.message.answer("🔥 Отлично! День засчитан. Увидимся завтра!", reply_markup=main_menu_kb())
