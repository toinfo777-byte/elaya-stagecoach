# app/routers/menu.py
from __future__ import annotations

from datetime import datetime, timedelta

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext

from app.storage.repo import session_scope
from app.storage.models import User, DrillRun

# тексты из system.py
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
@router.message(StateFilter("*"), Command("menu"))
async def open_menu(m: Message):
    await m.answer("Готово. Добро пожаловать в меню.", reply_markup=main_menu())

# ===== Тренировка дня =====
@router.message(StateFilter("*"), F.text == BTN_TRAIN)
async def menu_training(m: Message, state: FSMContext):
    await training_entry(m, state)

# ===== Мини-кастинг =====
@router.message(StateFilter("*"), F.text == BTN_CASTING)
async def menu_casting(m: Message, state: FSMContext):
    await casting_entry(m, state)

# ===== Политика =====
@router.message(StateFilter("*"), F.text == BTN_PRIVACY)
async def menu_privacy(m: Message):
    await m.answer(PRIVACY_TEXT)

# ===== Помощь =====
@router.message(StateFilter("*"), F.text == BTN_HELP)
async def menu_help(m: Message):
    await m.answer(HELP_TEXT)

# ===== Мой прогресс (не зависит от других роутеров) =====
@router.message(StateFilter("*"), F.text == BTN_PROGRESS)
async def menu_progress(m: Message):
    from app.storage.models import DrillRun  # локальный импорт, чтобы не плодить циклы
    def _pick_created_col():
        for name in ("created_at", "created", "created_dt", "timestamp", "ts", "inserted_at", "created_on"):
            if hasattr(DrillRun, name):
                return getattr(DrillRun, name)
        return None

    with session_scope() as s:
        u = s.query(User).filter_by(tg_id=m.from_user.id).first()
        if not u:
            await m.answer("Сначала пройди /start, а затем вернись в «Мой прогресс».", reply_markup=main_menu())
            return

        streak = u.streak or 0

        q = s.query(DrillRun).filter(DrillRun.user_id == u.id)
        created_col = _pick_created_col()
        if created_col is not None:
            since = datetime.utcnow() - timedelta(days=7)
            q = q.filter(created_col >= since)
        runs_7d = q.count()

    txt = (
        "📈 *Мой прогресс*\n\n"
        f"• Стрик: *{streak}*\n"
        f"• Этюдов за 7 дней: *{runs_7d}*\n\n"
        "Продолжай каждый день — тренировка дня в один клик 👇"
    )
    await m.answer(txt, reply_markup=main_menu(), parse_mode="Markdown")
