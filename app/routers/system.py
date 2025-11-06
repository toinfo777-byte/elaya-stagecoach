from __future__ import annotations

from aiogram import Router, types
from aiogram.filters import CommandStart, Command
from aiogram.types import ReplyKeyboardRemove

from app.config import settings

router = Router(name="system")


@router.message(CommandStart())
async def cmd_start(message: types.Message):
    # Профиль определяем через settings, безопасно с дефолтом
    profile = getattr(settings, "bot_profile", "hq")

    if profile == "hq":
        # Снимаем любое «прилипшее» меню
        await message.answer(
            "Привет! Я HQ-бот. Доступно: /status, /version, /panic.",
            reply_markup=ReplyKeyboardRemove(remove_keyboard=True),
        )
        return

    # --- профиль trainer: здесь высылаем ваше меню тренера ---
    # kb = build_trainer_keyboard()  # ваша функция
    # await message.answer("Меню тренировки:", reply_markup=kb)


@router.message(Command("menu"))
async def cmd_menu_clean(message: types.Message):
    """На всякий случай: команда для ручного снятия клавы в HQ."""
    profile = getattr(settings, "bot_profile", "hq")
    if profile == "hq":
        await message.answer("Клавиатура скрыта.", reply_markup=ReplyKeyboardRemove(True))
