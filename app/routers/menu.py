# app/routers/menu.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from app.keyboards.menu import (
    main_menu, small_menu,
    BTN_PROGRESS, BTN_POLICY, BTN_HELP, BTN_PREMIUM,
    BTN_SETTINGS,
)

router = Router(name="menu")


# ── Единый вход в меню (slash + текстовая кнопка + inline callback) ───────────

@router.message(Command("menu"))
async def open_menu(m: Message, state: FSMContext) -> None:
    await state.clear()
    await m.answer("Меню", reply_markup=main_menu())

@router.message(F.text == "Меню")  # на случай, если где-то осталась эта кнопка
async def menu_btn(m: Message, state: FSMContext):
    await state.clear()
    await m.answer("Готово! Открываю меню.", reply_markup=main_menu())

@router.callback_query(F.data == "menu:open")
async def menu_cb(c: CallbackQuery, state: FSMContext):
    await state.clear()
    await c.message.answer("Готово! Открываю меню.", reply_markup=main_menu())
    await c.answer()


# ── Остальные разделы меню ────────────────────────────────────────────────────

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
async def premium_preview(m: Message) -> None:
    await m.answer(
        "⭐ Расширенная версия\n\n• Больше сценариев тренировки\n• Персональные разборы\n• Расширенная метрика прогресса\n\n"
        "Пока это превью. Если интересно — напиши «Хочу расширенную» или жми /menu.",
        reply_markup=main_menu()
    )

@router.message(F.text == BTN_SETTINGS)
@router.message(Command("settings"))
async def open_settings(m: Message) -> None:
    await m.answer("Настройки. Можешь удалить профиль или вернуться в меню.", reply_markup=small_menu())
