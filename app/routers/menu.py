from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from app.keyboards.menu import (
    main_menu,
    BTN_TRAINING, BTN_PROGRESS, BTN_APPLY, BTN_CASTING,
    BTN_PRIVACY, BTN_HELP, BTN_SETTINGS, BTN_PREMIUM,
)

from app.routers.training import open_training
from app.routers.casting import open_casting
from app.routers.apply import open_apply

router = Router(name="menu")

@router.message(Command("menu"))
async def open_menu(m: Message):
    await m.answer("Меню", reply_markup=main_menu())

@router.message(F.text == BTN_TRAINING)
async def go_training(m: Message):
    await open_training(m, source="menu_button")

@router.message(F.text == BTN_PROGRESS)
async def go_progress(m: Message):
    await m.answer("Мой прогресс")

@router.message(F.text == BTN_APPLY)
async def go_apply(m: Message):
    await open_apply(m, source="menu_button")

@router.message(F.text == BTN_CASTING)
async def go_casting(m: Message):
    await open_casting(m, source="menu_button")

@router.message(F.text == BTN_PRIVACY)
async def go_privacy(m: Message):
    await m.answer("Политика конфиденциальности")

@router.message(F.text == BTN_HELP)
async def go_help(m: Message):
    await m.answer(
        "🆘 Помощь\n\nКоманды:\n"
        "/start — Начать / онбординг\n"
        "/menu — Открыть меню\n"
        "/training — Тренировка\n"
        "/progress — Мой прогресс\n"
        "/apply — Путь лидера (заявка)\n"
        "/privacy — Политика конфиденциальности\n"
        "/help — Помощь\n"
        "/settings — Настройки\n"
        "/cancel — Отмена",
    )

@router.message(F.text == BTN_SETTINGS)
async def go_settings(m: Message):
    await m.answer("Настройки. Можешь удалить профиль или вернуться в меню.")

@router.message(F.text == BTN_PREMIUM)
async def go_premium(m: Message):
    await m.answer("⭐ Расширенная версия")
