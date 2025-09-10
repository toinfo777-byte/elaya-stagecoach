# app/routers/menu.py
from __future__ import annotations

from datetime import datetime, timedelta

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext

from sqlalchemy import inspect as sqla_inspect
from sqlalchemy.sql.sqltypes import DateTime, Date

from app.storage.repo import session_scope
from app.storage.models import User, DrillRun

from app.routers.system import PRIVACY_TEXT, HELP_TEXT
from app.routers.training import training_entry
from app.routers.casting import casting_entry

router = Router(name="menu")

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

@router.message(StateFilter("*"), Command("menu"))
async def open_menu(m: Message):
    await m.answer("Готово. Добро пожаловать в меню.", reply_markup=main_menu())

@router.message(StateFilter("*"), F.text == BTN_TRAIN)
async def menu_training(m: Message, state: FSMContext):
    await training_entry(m, state)

@router.message(StateFilter("*"), F.text == BTN_CASTING)
async def menu_casting(m: Message, state: FSMContext):
    await casting_entry(m, state)

@router.message(StateFilter("*"), F.text == BTN_PRIVACY)
async def menu_privacy(m: Message):
    await m.answer(PRIVACY_TEXT)

@router.message(StateFilter("*"), F.text == BTN_HELP)
async def menu_help(m: Message):
    await m.answer(HELP_TEXT)

@router.message(StateFilter("*"), F.text == BTN_PROGRESS)
async def menu_progress(m: Message):
    with session_scope() as s:
        u = s.query(User).filter_by(tg_id=m.from_user.id).first()
        if not u:
            await m.answer("Сначала пройди /start, а затем вернись в «Мой прогресс».", reply_markup=main_menu())
            return

        streak = u.streak or 0
        q = s.query(DrillRun).filter(DrillRun.user_id == u.id)

        mapper = sqla_inspect(DrillRun)
        dt_col = next((c for c in mapper.columns if isinstance(c.type, (DateTime, Date))), None)

        if dt_col is not None:
            since = datetime.utcnow() - timedelta(days=7)
            runs_7d = q.filter(dt_col >= since).count()
        else:
            runs_7d = q.count()

        src_txt = ""
        try:
            meta = dict(u.meta_json or {}) if hasattr(u, "meta_json") else {}
            sources = meta.get("sources", {})
            first_src = sources.get("first_source")
            last_src = sources.get("last_source")
            if first_src or last_src:
                if first_src and last_src and first_src != last_src:
                    src_txt = f"\n• Источник: {first_src} → {last_src}"
                elif last_src:
                    src_txt = f"\n• Источник: {last_src}"
        except Exception:
            pass

    txt = (
        "📈 *Мой прогресс*\n\n"
        f"• Стрик: *{streak}*\n"
        f"• Этюдов за 7 дней: *{runs_7d}*"
        f"{src_txt}\n\n"
        "Продолжай каждый день — тренировка дня в один клик 👇"
    )
    await m.answer(txt, reply_markup=main_menu(), parse_mode="Markdown")
