# app/routers/menu.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from app.keyboards.menu import (
    main_menu, small_menu, to_menu_inline,
    BTN_PROGRESS, BTN_POLICY, BTN_HELP, BTN_PREMIUM,
    BTN_SETTINGS,
)

router = Router(name="menu")


@router.message(Command("menu"))
async def open_menu(m: Message) -> None:
    await m.answer("Меню", reply_markup=main_menu())


@router.message(F.text == BTN_PROGRESS)
@router.message(Command("progress"))
async def show_progress(m: Message) -> None:
    await m.answer(
        "📈 Мой прогресс\n\n• Стрик: 0\n• Этюдов за 7 дней: 0\n\n"
        "Продолжай каждый день — тренировка дня в один клик 👇",
        reply_markup=main_menu()
    )


@router.message(F.text == BTN_POLICY)
@router.message(Command("privacy"))
async def privacy(m: Message) -> None:
    await m.answer(
        "Политика конфиденциальности: мы бережно храним ваши данные и используем их только для работы бота.",
        reply_markup=main_menu()
    )


@router.message(F.text == BTN_HELP)
@router.message(Command("help"))
async def help_cmd(m: Message) -> None:
    await m.answer(
        "SOS Помощь\n\nКоманды:\n"
        "/start — Начать / онбординг\n"
        "/menu — Открыть меню\n"
        "/training — Тренировка\n"
        "/casting — Мини-кастинг\n"
        "/progress — Мой прогресс\n"
        "/apply — Путь лидера (заявка)\n"
        "/privacy — Политика\n"
        "/help — Помощь\n"
        "/settings — Настройки\n"
        "/cancel — Отмена",
        reply_markup=main_menu()
    )


@router.message(F.text == BTN_PREMIUM)
async def extended_offer(m: Message) -> None:
    await m.answer(
        "⭐ Расширенная версия:\n\n"
        "• Больше сценариев\n"
        "• Персональные разборы\n"
        "• Метрики прогресса\n\n"
        "Пока это оффер. Вернуться в меню можно кнопкой ниже 👇",
        reply_markup=to_menu_inline()
    )


@router.message(F.text == BTN_SETTINGS)
@router.message(Command("settings"))
async def open_settings(m: Message) -> None:
    await m.answer(
        "Настройки. Можешь удалить профиль или вернуться в меню.",
        reply_markup=small_menu()
    )

