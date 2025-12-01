from __future__ import annotations

from datetime import date

from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from app.keyboards.main_menu import MAIN_MENU
from app.training_progress import get_stats

router = Router(name="menu")

USER_ID = 1  # пока один пользователь — этого достаточно


# /start — приветствие и показ меню
@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    text = (
        "Привет! Я <b>🎭 Элайя · Тренер сцены</b>.\n\n"
        "Я здесь, чтобы поддерживать твой ритм практики:\n"
        "короткие тренировки, честная рефлексия и мягкое сопровождение.\n\n"
        "Нажми <b>«🎭 Тренировка дня»</b>, когда будешь готов."
    )
    await message.answer(text, reply_markup=MAIN_MENU)


# /menu — просто показать главное меню
@router.message(Command("menu"))
async def cmd_menu(message: Message) -> None:
    await message.answer("Главное меню открыто 👇", reply_markup=MAIN_MENU)


# 📈 Мой прогресс
@router.message(F.text == "📈 Мой прогресс")
async def btn_progress(message: Message) -> None:
    stats = get_stats(USER_ID)
    total = stats.get("total", 0)
    today_count = stats.get("by_date", {}).get(date.today().isoformat(), 0)

    text = (
        "📈 <b>Твой прогресс</b>\n\n"
        f"Всего завершено тренировок: <b>{total}</b>\n"
        f"Сегодня: <b>{today_count}</b>\n\n"
        "Пока это базовая статистика.\n"
        "Дальше здесь появится более детальный и красивый отчёт."
    )
    await message.answer(text, reply_markup=MAIN_MENU)


# 💬 Помощь
@router.message(F.text == "💬 Помощь")
async def btn_help(message: Message) -> None:
    text = (
        "💬 <b>Помощь</b>\n\n"
        "— Нажимай <b>«🎭 Тренировка дня»</b>, когда хочешь пройти короткую практику.\n"
        "— После практики я помогу зафиксировать состояние и маленький шаг.\n"
        "— Через <b>«📈 Мой прогресс»</b> можно смотреть, как ты держишь ритм.\n\n"
        "Если что-то сломалось или есть идеи — просто напиши мне сюда текстом."
    )
    await message.answer(text, reply_markup=MAIN_MENU)


# 🔐 Политика
@router.message(F.text == "🔐 Политика")
async def btn_policy(message: Message) -> None:
    text = (
        "🔐 <b>Политика тренера</b>\n\n"
        "— Я не собираю и не анализирую личные данные вне тренировок.\n"
        "— Всё, что ты пишешь, используется только для улучшения практики\n"
        "  и отражения в твоём личном прогрессе.\n\n"
        "Если появится отдельная публичная политика — ссылка появится здесь."
    )
    await message.answer(text, reply_markup=MAIN_MENU)


# ⭐️ Расширенная версия
@router.message(F.text == "⭐️ Расширенная версия")
async def btn_extended(message: Message) -> None:
    text = (
        "⭐️ <b>Расширенная версия Элайя · Тренер</b>\n\n"
        "Здесь появятся:\n"
        "— индивидуальные программы\n"
        "— сцены и модули под разные задачи\n"
        "— глубокие разборы практики и прогресса\n\n"
        "Пока это в разработке. Ты уже на базовом уровне, который станет ядром."
    )
    await message.answer(text, reply_markup=MAIN_MENU)
