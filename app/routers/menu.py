# app/routers/menu.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.keyboards.reply import (
    main_menu_kb,
    BTN_PROGRESS, BTN_POLICY, BTN_HELP, BTN_EXTENDED, BTN_SETTINGS,
)

router = Router(name="menu")

@router.message(StateFilter("*"), Command("menu"))
async def open_menu(m: Message, state: FSMContext) -> None:
    await state.clear()
    await m.answer("Готово! Открываю меню.", reply_markup=main_menu_kb())

# Оставляем здесь только «быстрые» тексты. Детальные — в соответствующих роутерах.
@router.message(StateFilter("*"), F.text == BTN_EXTENDED)
async def extended_offer(m: Message) -> None:
    await m.answer(
        "⭐ Расширенная версия:\n\n"
        "• Больше сценариев\n"
        "• Персональные разборы\n"
        "• Метрики прогресса\n\n"
        "Пока это оффер. Вернуться в меню можно кнопкой ниже 👇",
        reply_markup=main_menu_kb()
    )

@router.message(StateFilter("*"), F.text == BTN_HELP)
@router.message(StateFilter("*"), Command("help"))
async def help_redirect(m: Message) -> None:
    # перенаправляем к экрану помощи с инлайн-кнопками
    from app.routers.help import help_cmd
    await help_cmd(m, )  # state не обязателен, наш хендлер сам справится

@router.message(StateFilter("*"), F.text == BTN_PROGRESS)
@router.message(StateFilter("*"), Command("progress"))
async def show_progress(m: Message) -> None:
    await m.answer(
        "📈 Мой прогресс\n\n• Стрик: 0\n• Этюдов за 7 дней: 0\n\n"
        "Продолжай каждый день — тренировка дня в один клик 👇",
        reply_markup=main_menu_kb()
    )
