# app/bot/routers/premium.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from app.keyboards.menu import main_menu, BTN_PREMIUM

router = Router(name="premium")

# Локальная клавиатура раздела (для шага внутри premium)
def _premium_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔎 Что внутри?")],
            [KeyboardButton(text="📝 Оставить заявку")],
            [KeyboardButton(text="🧭 В меню")],
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
    )

@router.message(Command("premium"))
@router.message(F.text == BTN_PREMIUM)
async def premium_entry(message: Message) -> None:
    text = (
        "<b>⭐️ Расширенная версия</b>\n\n"
        "• Ежедневный разбор и обратная связь\n"
        "• Разогрев голоса, дикции и внимания\n"
        "• Мини-кастинг и «путь лидера»\n\n"
        "Выберите действие:"
    )
    await message.answer(text, reply_markup=_premium_kb())

@router.message(F.text == "🔎 Что внутри?")
async def premium_inside(message: Message) -> None:
    await message.answer(
        "Внутри расширенной версии — больше практики и персональных разборов.",
        reply_markup=_premium_kb(),
    )

@router.message(F.text == "📝 Оставить заявку")
async def premium_ask_goal(message: Message) -> None:
    await message.answer(
        "Напишите цель одной короткой фразой (до 200 символов). "
        "Если передумали — отправьте /cancel.",
        reply_markup=ReplyKeyboardRemove(),
    )

@router.message(F.text == "🧭 В меню")
async def premium_back_to_menu(message: Message) -> None:
    await message.answer("Ок, вернулись в главное меню. Нажми нужную кнопку снизу.", reply_markup=main_menu())

# Пришёл свободный текст — считаем это заявкой (если человек в премиуме)
@router.message(F.text.func(lambda t: t not in {BTN_PREMIUM, "🔎 Что внутри?", "📝 Оставить заявку", "🧭 В меню"}))
async def premium_save_goal(message: Message) -> None:
    # здесь можно записать заявку в БД
    await message.answer("Спасибо! Принял. Двигаемся дальше 👍", reply_markup=main_menu())
