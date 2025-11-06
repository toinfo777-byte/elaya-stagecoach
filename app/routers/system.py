from __future__ import annotations

from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from app.config import settings

router = Router(name="system")


@router.message(CommandStart())
async def cmd_start(message: types.Message) -> None:
    # HQ-профиль — НИКАКИХ клавиатур
    if settings.bot_profile == "hq":
        await message.answer(
            "Привет! Я HQ-бот. Доступно: /status, /version, /panic."
        )
        return

    # trainer-профиль — можно показать простое меню (без внешних зависимостей)
    try:
        # если в проекте есть «настоящее» меню, можно аккуратно попытаться его подключить
        # from app.routers.training import main_menu_kb  # пример
        # kb = main_menu_kb()
        kb = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="🏋️ Тренировка дня"), KeyboardButton(text="📈 Мой прогресс")],
                [KeyboardButton(text="🎯 Путь лидера"), KeyboardButton(text="⚙️ Настройки")],
                [KeyboardButton(text="⭐ Расширенная версия")],
            ],
            resize_keyboard=True,
        )
    except Exception:
        kb = None

    if kb:
        await message.answer("Меню тренировки:", reply_markup=kb)
    else:
        await message.answer("Меню тренировки активно.")
