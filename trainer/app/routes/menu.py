# trainer/app/routes/menu.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from ..training_progress import get_progress_summary

router = Router(name="menu")

# --- Главное меню тренера -------------------------------------------

MAIN_MENU = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🎭 Тренировка дня"),
        ],
        [
            KeyboardButton(text="📈 Мой прогресс"),
            KeyboardButton(text="💬 Помощь"),
        ],
        [
            KeyboardButton(text="⭐️ Расширенная версия"),
        ],
    ],
    resize_keyboard=True,
)


# --- /start ---------------------------------------------------------


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    """
    Базовая точка входа.
    """
    await state.clear()

    await message.answer(
        "Привет. Я — Элайя, тренер сцены.\n\n"
        "• Нажимай «🎭 Тренировка дня», чтобы пройти 4 шага.\n"
        "• «📈 Мой прогресс» — посмотреть статистику.\n"
        "• «💬 Помощь» — подсказка по командам.",
        reply_markup=MAIN_MENU,
    )


# --- Мой прогресс ---------------------------------------------------


@router.message(F.text == "📈 Мой прогресс")
async def cmd_progress(message: Message) -> None:
    """
    Показываем сводку по тренировкам.
    FSM-состояние не меняем.
    """
    summary = get_progress_summary(user_id=message.from_user.id)

    if not summary:
        summary = (
            "Пока нет сохранённых тренировок.\n"
            "Попробуй пройти первую — нажимай «🎭 Тренировка дня»."
        )

    await message.answer(summary, reply_markup=MAIN_MENU)


# --- Помощь ---------------------------------------------------------


@router.message(F.text == "💬 Помощь")
async def cmd_help(message: Message) -> None:
    await message.answer(
        "Я веду тренировку сцены в формате короткой рефлексии.\n\n"
        "• «🎭 Тренировка дня» — 4 шага (вход, отражение, шаг, финальное слово).\n"
        "• «📈 Мой прогресс» — сводка по дням.\n"
        "• «⭐️ Расширенная версия» — в разработке.",
        reply_markup=MAIN_MENU,
    )


# --- Расширенная версия (заглушка) ----------------------------------


@router.message(F.text == "⭐️ Расширенная версия")
async def cmd_premium(message: Message) -> None:
    await message.answer(
        "Расширенная версия ещё в разработке.\n"
        "Когда она появится — ты узнаешь об этом здесь.",
        reply_markup=MAIN_MENU,
    )
