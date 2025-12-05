# trainer/app/routes/menu.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart  # <-- новый импорт

from .keyboards import (
    MAIN_MENU,
    BTN_PROGRESS,
    BTN_HELP,
    BTN_PREMIUM,
    BTN_TRAINING_DAY,
)

router = Router()


@router.message(CommandStart())  # <-- вместо commands={"start"}
async def cmd_start(message: Message) -> None:
    """
    Старт бота: просто показываем главное меню.
    """
    await message.answer(
        "Элайя — Тренер сцены.\n\n"
        "Нажимай «🎭 Тренировка дня», чтобы пройти сегодняшнюю настройку.\n"
        "Или выбери другую кнопку внизу.",
        reply_markup=MAIN_MENU,
    )


@router.message(F.text == BTN_PROGRESS)
async def show_progress_entry(message: Message) -> None:
    # пока просто заглушка, чтобы бот не молчал
    await message.answer(
        "Я пока считаю твой прогресс, но API ядра уже подключено. "
        "Скоро здесь будет красивая сводка ❤️",
        reply_markup=MAIN_MENU,
    )


@router.message(F.text == BTN_HELP)
async def show_help(message: Message) -> None:
    await message.answer(
        "Помощь тренера.\n\n"
        "1) Нажимаешь «🎭 Тренировка дня».\n"
        "2) Отвечаешь честно на 4 вопроса.\n"
        "3) Я фиксирую твой день и возвращаю в главное меню.",
        reply_markup=MAIN_MENU,
    )


@router.message(F.text == BTN_PREMIUM)
async def premium_stub(message: Message) -> None:
    await message.answer(
        "⭐️ Расширенная версия ещё в разработке.\n"
        "Ты уже в ядре проекта Элайи, так что увидишь её одним из первых.",
        reply_markup=MAIN_MENU,
    )
