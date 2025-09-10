# app/routers/shortcuts.py
from __future__ import annotations

from datetime import datetime, timedelta

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.types import Message

from aiogram.fsm.context import FSMContext

from app.storage.repo import session_scope
from app.storage.models import User, DrillRun

# тексты
from app.routers.system import PRIVACY_TEXT, HELP_TEXT

# входы фич
from app.routers.training import training_entry
from app.routers.casting import casting_entry

router = Router(name="shortcuts")

# Тексты кнопок (синхронизированы с menu.py и coach._MENU_TEXTS)
BTN_TRAIN = "🎯 Тренировка дня"
BTN_PROGRESS = "📈 Мой прогресс"
BTN_APPLY = "Путь лидера"
BTN_CASTING = "🎭 Мини-кастинг"
BTN_PRIVACY = "🔐 Политика"
BTN_HELP = "💬 Помощь"

# === Глобальные обработчики (в любом состоянии), срабатывают ДО онбординга ===

@router.message(StateFilter("*"), F.text == BTN_TRAIN)
async def sc_training(m: Message, state: FSMContext):
    await training_entry(m, state)

@router.message(StateFilter("*"), F.text == BTN_CASTING)
async def sc_casting(m: Message, state: FSMContext):
    await casting_entry(m, state)

@router.message(StateFilter("*"), F.text == BTN_PRIVACY)
async def sc_privacy(m: Message):
    await m.answer(PRIVACY_TEXT)

@router.message(StateFilter("*"), F.text == BTN_HELP)
async def sc_help(m: Message):
    await m.answer(HELP_TEXT)

@router.message(StateFilter("*"), F.text == BTN_PROGRESS)
async def sc_progress(m: Message):
    # короткий отчёт как в меню
    from app.routers.menu import main_menu  # локальный импорт, чтобы избежать циклов
    with session_scope() as s:
        u = s.query(User).filter_by(tg_id=m.from_user.id).first()
        if not u:
            await m.answer("Сначала пройди /start, а затем вернись в «Мой прогресс».", reply_markup=main_menu())
            return

        streak = u.streak or 0
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
