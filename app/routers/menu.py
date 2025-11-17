# app/routers/menu.py
from aiogram import Router, F
from aiogram.types import Message

from app.keyboards.main_menu import MAIN_MENU

router = Router(name="menu-router")


@router.message(F.text == "/menu")
async def cmd_menu(message: Message):
    await message.answer("Главное меню Элайи — тренера сцены:", reply_markup=MAIN_MENU)


@router.message(F.text == "🏋️‍♂️ Тренировка дня")
async def handle_training(message: Message):
    # пока заглушка; здесь потом будут сцены тренировки
    await message.answer(
        "Здесь будет твоя тренировка дня.\n"
        "Пока что я готовлю программу упражнений ✨",
        reply_markup=MAIN_MENU,
    )
