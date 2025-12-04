from __future__ import annotations

from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from ..training_progress import get_progress_summary

# --- Главное меню тренера -------------------------------------------------

MAIN_MENU = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🎭 Тренировка дня")],
        [
            KeyboardButton(text="📈 Мой прогресс"),
            KeyboardButton(text="💬 Помощь"),
        ],
        [
            KeyboardButton(text="🔐 Политика"),
            KeyboardButton(text="⭐️ Расширенная версия"),
        ],
    ],
    resize_keyboard=True,
)

router = Router(name="menu")


# --- Обработчик "Мой прогресс" -------------------------------------------


@router.message(F.text == "📈 Мой прогресс")
async def handle_progress(message: Message) -> None:
    """
    Показываем простой прогресс по локальным данным тренера.
    (Для локального запуска — JSON в trainer/app/data/training_progress.json)
    """
    stats = get_progress_summary(user_id=1)  # пока один пользователь

    total = stats["total_days"]
    streak = stats["current_streak"]
    last_date = stats["last_date"]

    lines = [
        f"Всего завершено тренировок: {total}",
        f"Текущая серия по дням: {streak}",
    ]

    if last_date:
        lines.append(f"Последний завершённый день: {last_date}")
    else:
        lines.append("Пока ещё нет завершённых тренировок.")

    lines.append("")
    lines.append("Даже одна короткая тренировка в день — уже движение вперёд.")

    await message.answer("\n".join(lines), reply_markup=MAIN_MENU)


# --- Обработчик 'Помощь' --------------------------------------------------


@router.message(F.text == "💬 Помощь")
async def handle_help(message: Message) -> None:
    await message.answer(
        "Я — тренер сцены Элайи.\n\n"
        "Нажимай «🎭 Тренировка дня», проходи шаги и в конце пиши короткое "
        "финальное слово. Кнопка «📈 Мой прогресс» покажет общую динамику.\n\n"
        "Остальные кнопки пока-заглушки и будут постепенно наполняться.",
        reply_markup=MAIN_MENU,
    )


# --- Обработчик 'Политика' -----------------------------------------------


@router.message(F.text == "🔐 Политика")
async def handle_policy(message: Message) -> None:
    await message.answer(
        "Политика конфиденциальности:\n\n"
        "Все ответы тренировки используются только для твоего прогресса "
        "и развития проекта Элайи. Никаких публичных публикаций без "
        "твоего отдельного согласия.",
        reply_markup=MAIN_MENU,
    )


# --- Обработчик 'Расширенная версия' --------------------------------------


@router.message(F.text == "⭐️ Расширенная версия")
async def handle_pro(message: Message) -> None:
    await message.answer(
        "Расширенная версия тренера пока в разработке.\n"
        "Здесь появятся дополнительные форматы тренировок и сцены.",
        reply_markup=MAIN_MENU,
    )
