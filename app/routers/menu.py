# app/routers/menu.py
from __future__ import annotations

from datetime import datetime, timedelta

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from app.storage.repo import session_scope
from app.storage.models import User, DrillRun

# берём тексты прямо из system.py
from app.routers.system import PRIVACY_TEXT, HELP_TEXT

# «входы» фич
from app.routers.training import training_entry
from app.routers.casting import casting_entry

router = Router(name="menu")

# Тексты кнопок меню (синхронизированы с coach._MENU_TEXTS)
BTN_TRAIN = "🎯 Тренировка дня"
BTN_PROGRESS = "📈 Мой прогресс"
BTN_APPLY = "Путь лидера"
BTN_CASTING = "🎭 Мини-кастинг"
BTN_PRIVACY = "🔐 Политика"
BTN_HELP = "💬 Помощь"

def main_menu() -> ReplyKeyboardMarkup:
    # широкая первая строка + две «узкие» ниже
    return ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [KeyboardButton(text=BTN_TRAIN), KeyboardButton(text=BTN_PROGRESS)],
            [KeyboardButton(text=BTN_APPLY)],
            [KeyboardButton(text=BTN_CASTING)],
            [KeyboardButton(text=BTN_PRIVACY), KeyboardButton(text=BTN_HELP)],
        ],
    )

# ===== /menu =====
@router.message(Command("menu"))
async def open_menu(m: Message):
    await m.answer("Готово. Добро пожаловать в меню.", reply_markup=main_menu())


# ===== Тренировка дня =====
@router.message(F.text == BTN_TRAIN)
async def menu_training(m: Message):
    # просто вызываем «вход» тренировки
    from aiogram.fsm.context import FSMContext  # локальный импорт, чтобы не тянуть лишнее
    state = FSMContext(storage=m.bot.dispatcher.storage, chat=m.chat, user=m.from_user)
    await training_entry(m, state)


# ===== Мини-кастинг =====
@router.message(F.text == BTN_CASTING)
async def menu_casting(m: Message):
    from aiogram.fsm.context import FSMContext
    state = FSMContext(storage=m.bot.dispatcher.storage, chat=m.chat, user=m.from_user)
    await casting_entry(m, state)


# ===== Политика =====
@router.message(F.text == BTN_PRIVACY)
async def menu_privacy(m: Message):
    await m.answer(PRIVACY_TEXT)


# ===== Помощь =====
@router.message(F.text == BTN_HELP)
async def menu_help(m: Message):
    await m.answer(HELP_TEXT)


# ===== Мой прогресс (не зависит от других роутеров) =====
@router.message(F.text == BTN_PROGRESS)
async def menu_progress(m: Message):
    """
    Короткий самостоятельный отчёт:
    - текущий стрик пользователя (если есть в таблице users)
    - сколько этюдов выполнено за последние 7 дней (по DrillRun)
    """
    with session_scope() as s:
        u = s.query(User).filter_by(tg_id=m.from_user.id).first()
        if not u:
            await m.answer("Сначала пройди /start, а затем вернись в «Мой прогресс».", reply_markup=main_menu())
            return

        # стрик
        streak = u.streak or 0

        # этюды за 7 дней
        since = datetime.utcnow() - timedelta(days=7)
        runs_7d = (
            s.query(DrillRun)
            .filter(DrillRun.user_id == u.id, DrillRun.created_at >= since)
            .count()
        )

    txt = (
        "📈 *Мой прогресс*\n\n"
        f"• Стрик: *{streak}*\n"
        f"• Этюдов за 7 дней: *{runs_7d}*\n\n"
        "Продолжай каждый день — тренировка дня в один клик 👇"
    )
    await m.answer(txt, reply_markup=main_menu(), parse_mode="Markdown")
