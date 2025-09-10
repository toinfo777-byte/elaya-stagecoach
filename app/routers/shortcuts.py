# app/routers/shortcuts.py
from __future__ import annotations

from datetime import datetime, timedelta

from aiogram import Router, F
from aiogram.filters import StateFilter, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.routers.system import PRIVACY_TEXT, HELP_TEXT
from app.routers.training import training_entry
from app.routers.casting import casting_entry
from app.storage.repo import session_scope
from app.storage.models import User, DrillRun

# ⚠️ берём тексты прямо из menu.py, чтобы не было рассинхрона
from app.routers.menu import (
    BTN_TRAIN,
    BTN_PROGRESS,
    BTN_APPLY,         # не используем, но оставил для симметрии
    BTN_CASTING,
    BTN_PRIVACY,
    BTN_HELP,
    main_menu,         # используем в _send_progress
)

router = Router(name="shortcuts")

# ===== Команды в любом состоянии (срабатывают ДО онбординга) =====
@router.message(StateFilter("*"), Command("help"))
async def sc_help_cmd(m: Message):
    await m.answer(HELP_TEXT)

@router.message(StateFilter("*"), Command("privacy"))
async def sc_privacy_cmd(m: Message):
    await m.answer(PRIVACY_TEXT)

@router.message(StateFilter("*"), Command("progress"))
async def sc_progress_cmd(m: Message):
    await _send_progress(m)

# ===== Текстовые кнопки в любом состоянии =====
@router.message(StateFilter("*"), F.text == BTN_TRAIN)
async def sc_training(m: Message, state: FSMContext):
    await training_entry(m, state)

@router.message(StateFilter("*"), F.text == BTN_CASTING)
async def sc_casting(m: Message, state: FSMContext):
    await casting_entry(m, state)

@router.message(StateFilter("*"), F.text == BTN_PRIVACY)
async def sc_privacy_text(m: Message):
    await m.answer(PRIVACY_TEXT)

@router.message(StateFilter("*"), F.text == BTN_HELP)
async def sc_help_text(m: Message):
    await m.answer(HELP_TEXT)

# — основной точный матч
@router.message(StateFilter("*"), F.text == BTN_PROGRESS)
async def sc_progress_text_exact(m: Message):
    await _send_progress(m)

# — «фаззи» подстраховка (если вдруг другая раскладка/эмодзи/пробелы)
@router.message(StateFilter("*"), lambda m: isinstance(m.text, str) and "прогресс" in m.text.lower())
async def sc_progress_text_fuzzy(m: Message):
    await _send_progress(m)

# ===== Реализация «Мой прогресс» =====
async def _send_progress(m: Message):
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
