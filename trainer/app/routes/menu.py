from __future__ import annotations

from typing import Any, Dict

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from app.core_client import fetch_progress

router = Router()


# --- Клавиатура ---------------------------------------------------------------

MAIN_MENU = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🎭 Тренировка дня")],
        [
            KeyboardButton(text="📈 Мой прогресс"),
            KeyboardButton(text="💬 Помощь"),
        ],
        [KeyboardButton(text="⭐️ Расширенная версия")],
    ],
    resize_keyboard=True,
)


# --- Хендлеры -----------------------------------------------------------------


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """
    Стартовое приветствие + показ нижнего меню.
    """
    await message.answer(
        "Элайя — Тренер сцены.\n\n"
        "Нажимай «🎭 Тренировка дня», чтобы пройти сегодняшнюю настройку.\n"
        "Или выбери другую кнопку внизу.",
        reply_markup=MAIN_MENU,
    )


@router.message(F.text == "📈 Мой прогресс")
async def handle_progress(message: Message) -> None:
    """
    Краткая сводка прогресса из ядра.
    Если ядро не настроено / не отвечает — даём мягкий fallback.
    """
    user_id = message.from_user.id if message.from_user else 0

    data: Dict[str, Any] = await fetch_progress(user_id=user_id, limit=7)
    if not data:
        await message.answer(
            "Пока я не вижу сохранённых тренировок.\n"
            "Пройди хотя бы одну — и я начну считать серию.",
            reply_markup=MAIN_MENU,
        )
        return

    total_days = data.get("total_days", 0)
    current_streak = data.get("current_streak", 0)

    text = (
        "📈 Твой прогресс:\n\n"
        f"• Всего тренировочных дней: <b>{total_days}</b>\n"
        f"• Текущая серия: <b>{current_streak}</b> дней\n\n"
        "Продолжай в том же духе. Если захочешь — нажимай «🎭 Тренировка дня»."
    )

    await message.answer(text, reply_markup=MAIN_MENU)


@router.message(F.text == "💬 Помощь")
async def handle_help(message: Message) -> None:
    await message.answer(
        "Я — тренер практики присутствия.\n\n"
        "Каждый день я задаю 3 простых вопроса:\n"
        "1) В каком состоянии ты входишь в день.\n"
        "2) Как ты видишь свой день со стороны.\n"
        "3) Какой маленький шаг готов сделать.\n\n"
        "Нажимай «🎭 Тренировка дня», чтобы пройти настройку.",
        reply_markup=MAIN_MENU,
    )


@router.message(F.text == "⭐️ Расширенная версия")
async def handle_premium(message: Message) -> None:
    await message.answer(
        "Расширенная версия Элайи пока в разработке.\n"
        "Ты уже в числе первых, кто тестирует тренера.",
        reply_markup=MAIN_MENU,
    )
