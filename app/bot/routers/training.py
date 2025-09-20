from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from app.keyboards.menu import main_menu, BTN_TRAIN

router = Router(name="training")

# Демонстрационный сценарий «этюд дня»
_ETUDS = [
    "Этюд: Три мягких зевка\nШаг 1/4:\nЗевок 1",
    "Этюд: Три мягких зевка\nШаг 2/4:\nЗевок 2",
    "Этюд: Три мягких зевка\nШаг 3/4:\nЗевок 3",
    "Этюд: Три мягких зевка\nШаг 4/4:\nЗаверши дыханием",
]

def _controls(step: int) -> InlineKeyboardMarkup:
    next_btn = InlineKeyboardButton(text="Далее ▶️", callback_data=f"train:next:{step}")
    skip_btn = InlineKeyboardButton(text="Пропустить ⏭", callback_data=f"train:skip:{step}")
    done_btn = InlineKeyboardButton(text="Готово ✅", callback_data=f"train:done:{step}")
    return InlineKeyboardMarkup(inline_keyboard=[
        [next_btn],
        [skip_btn, done_btn],
    ])

@router.message(Command("training"))
@router.message(F.text == BTN_TRAIN)
async def training_entry(message: Message) -> None:
    text = "🧭 Тренировка дня"
    await message.answer(text, reply_markup=main_menu())
    await message.answer(_ETUDS[0], reply_markup=_controls(0))

# Колбэки можно оставить как есть, но каждое сообщение тоже сопровождаем main_menu()
from aiogram.types import CallbackQuery

@router.callback_query(F.data.startswith("train:"))
async def training_callbacks(cb: CallbackQuery) -> None:
    _, action, raw = cb.data.split(":")
    step = int(raw)

    if action == "next":
        step = min(step + 1, len(_ETUDS) - 1)
        await cb.message.edit_text(_ETUDS[step], reply_markup=_controls(step))
    elif action == "skip":
        step = min(step + 1, len(_ETUDS) - 1)
        await cb.answer("Шаг пропущен")
        await cb.message.edit_reply_markup(reply_markup=_controls(step))
    elif action == "done":
        await cb.answer("Отлично!")
        await cb.message.delete()

    # Подстраховка: актуализируем нижнее меню
    try:
        await cb.message.answer("Продолжай каждый день — тренировка дня в один клик 👇", reply_markup=main_menu())
    except Exception:
        pass
