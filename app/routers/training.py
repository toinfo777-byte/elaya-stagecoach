# app/routers/training.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from app.keyboards.reply import main_menu_kb

router = Router(name="training")

def levels_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Уровень 1"), KeyboardButton(text="Уровень 2")],
            [KeyboardButton(text="🏠 В меню")],
        ],
        resize_keyboard=True
    )

def l1_steps_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Выполнил(а)"),
             KeyboardButton(text="↩️ Назад к уровням")],
            [KeyboardButton(text="🏠 В меню")],
        ],
        resize_keyboard=True
    )

@router.message(Command("levels"))
@router.message(StateFilter("*"), F.text == "🏋️ Тренировка дня")
async def show_training_levels(msg: Message):
    await msg.answer(
        "🏋️ <b>Тренировка дня</b>\n\nВыбери уровень — внутри подробные шаги.",
        reply_markup=levels_kb()
    )

@router.message(StateFilter("*"), F.text == "Уровень 1")
@router.message(Command("training"))
async def level1(msg: Message):
    await msg.answer(
        "📗 <b>Уровень 1</b>\n\n"
        "1) 30 сек тишины и дыхание.\n"
        "2) 3 фразы с паузой 2 сек.\n"
        "3) Повтори ещё раз.\n\n"
        "Когда закончишь — нажми «✅ Выполнил(а)».",
        reply_markup=l1_steps_kb()
    )

@router.message(StateFilter("*"), F.text == "✅ Выполнил(а)")
async def done_level(msg: Message):
    await msg.answer("Круто! Записал — продолжай каждый день.", reply_markup=main_menu_kb())

@router.message(StateFilter("*"), F.text == "↩️ Назад к уровням")
async def back_to_levels(msg: Message):
    await show_training_levels(msg)

@router.message(StateFilter("*"), F.text == "🏠 В меню")
async def back_home(msg: Message):
    await msg.answer("Вернул в меню.", reply_markup=main_menu_kb())
