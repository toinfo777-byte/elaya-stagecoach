from aiogram import Router, F
from aiogram.types import Message

from app.keyboards.main_menu import MAIN_MENU, BTN_TRAINING

router = Router(name="menu-router")


@router.message(F.text == "/menu")
async def cmd_menu(message: Message) -> None:
    """Команда /menu — просто открыть главное меню."""
    await message.answer(
        "Главное меню Элайи — тренера сцены:",
        reply_markup=MAIN_MENU,
    )


@router.message(F.text == BTN_TRAINING)
async def handle_training(message: Message) -> None:
    """
    Вход в тренировку дня.
    Пока что — заглушка, дальше сюда прикрутим реальные сцены.
    """
    await message.answer(
        "Здесь будет твоя тренировка дня.\n"
        "Пока что я готовлю программу упражнений ✨",
        reply_markup=MAIN_MENU,
    )
