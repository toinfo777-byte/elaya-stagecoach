# trainer/app/routes/menu.py
from __future__ import annotations

import logging

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
)

from app.core_client import fetch_progress
from .training_flow import start_training

router = Router(name="menu")
logger = logging.getLogger(__name__)

# --- Клавиатура главного меню ------------------------------------

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


# --- Старт тренировки --------------------------------------------

@router.message(CommandStart())
@router.message(F.text == "🎭 Тренировка дня")
async def handle_start(message: Message, state: FSMContext) -> None:
    """
    /start и кнопка «🎭 Тренировка дня» — запускают сценарий тренировки.
    """
    await start_training(message, state)


# --- Мой прогресс ------------------------------------------------

@router.message(F.text == "📈 Мой прогресс")
async def handle_progress(message: Message) -> None:
    """
    Кнопка «📈 Мой прогресс» — сводка по недавним тренировкам пользователя.
    """
    user_id = message.from_user.id

    try:
        data = await fetch_progress(user_id=user_id, limit=7)
    except Exception:
        logger.exception("Failed to fetch progress for user %s", user_id)
        await message.answer(
            "Не получилось получить прогресс.\n"
            "Попробуй ещё раз чуть позже.",
            reply_markup=MAIN_MENU,
        )
        return

    if not data or data.get("status") != "ok":
        await message.answer(
            "Пока не удалось получить прогресс.\n"
            "Попробуй чуть позже.",
            reply_markup=MAIN_MENU,
        )
        return

    total_days = data.get("total_days", 0)
    last_date = data.get("last_date") or {}
    days_raw = data.get("days") or {}

    lines: list[str] = []

    lines.append("📈 <b>Твой прогресс</b>")
    lines.append("")

    if total_days <= 0:
        lines.append("Пока нет завершённых тренировок.")
        lines.append("Нажимай «🎭 Тренировка дня», чтобы начать.")
        await message.answer("\n".join(lines), reply_markup=MAIN_MENU)
        return

    lines.append(f"Всего тренированных дней: <b>{total_days}</b>")

    # last_date может быть либо словарём, либо пустым {}
    ld_date = last_date.get("date") if isinstance(last_date, dict) else None
    if ld_date:
        lines.append(f"Последняя тренировка: <b>{ld_date}</b>")

    # Универсальная обработка: поддерживаем и dict, и list
    days_list: list[dict] = []
    if isinstance(days_raw, dict):
        # формат: {"2025-12-04": {...}, ...}
        for d, v in sorted(days_raw.items(), reverse=True):
            day_data = dict(v or {})
            day_data.setdefault("date", d)
            days_list.append(day_data)
    elif isinstance(days_raw, list):
        days_list = [d for d in days_raw if isinstance(d, dict)]

    if days_list:
        lines.append("")
        lines.append("Последние дни:")

        for day in days_list:
            d_date = day.get("date", "—")

            vector = day.get("vector") or "—"
            reflect = day.get("reflect") or "—"
            transition = day.get("transition") or "—"
            review = day.get("review") or "—"

            # один блок на день
            lines.append(
                f"\n🗓 <b>{d_date}</b>\n"
                f"  🎯 Вектор: {vector}\n"
                f"  🪞 Отражение: {reflect}\n"
                f"  🔁 Шаг: {transition}\n"
                f"  📝 Слово дня: {review}"
            )

    await message.answer(
        "\n".join(lines),
        reply_markup=MAIN_MENU,
    )


# --- Помощь и расширенная версия (заглушки) ----------------------

@router.message(F.text == "💬 Помощь")
async def handle_help(message: Message) -> None:
    await message.answer(
        "Я веду тренировки сцены в формате короткой рефлексии.\n"
        "• «🎭 Тренировка дня» — 4 шага (вход, отражение, шаг, финальное слово).\n"
        "• «📈 Мой прогресс» — сводка по дням.\n"
        "Расширенная версия — в разработке.",
        reply_markup=MAIN_MENU,
    )


@router.message(F.text == "⭐️ Расширенная версия")
async def handle_extended(message: Message) -> None:
    await message.answer(
        "Расширенная версия ещё в разработке.\n"
        "Когда она появится — ты узнаешь об этом здесь.",
        reply_markup=MAIN_MENU,
    )
