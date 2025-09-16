# app/routers/shortcuts.py
from __future__ import annotations

from datetime import datetime, timedelta

from aiogram import Router, F
from aiogram.filters import StateFilter, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from sqlalchemy import inspect as sqla_inspect
from sqlalchemy.sql.sqltypes import DateTime, Date

from app.routers.system import PRIVACY_TEXT, HELP_TEXT
from app.routers.training import training_entry
from app.routers.casting import casting_entry
from app.storage.repo import session_scope
from app.storage.models import User, DrillRun
from app.bot.states import ApplyStates
from app.routers.menu import (
    BTN_TRAIN,
    BTN_PROGRESS,
    BTN_APPLY,
    BTN_CASTING,
    BTN_PRIVACY,
    BTN_HELP,
    main_menu,
)

router = Router(name="shortcuts")


# ===== команды, которые должны работать в ЛЮБОМ состоянии =====
@router.message(StateFilter("*"), Command("help"))
async def sc_help_cmd(m: Message):
    await m.answer(HELP_TEXT)


@router.message(StateFilter("*"), Command("privacy"))
async def sc_privacy_cmd(m: Message):
    await m.answer(PRIVACY_TEXT)


@router.message(StateFilter("*"), Command("progress"))
async def sc_progress_cmd(m: Message):
    await _send_progress(m)


# 🔧 ДОБАВЛЕНО: ловим /training и /casting ещё ДО онбординга
@router.message(StateFilter("*"), Command("training"))
async def sc_training_cmd(m: Message, state: FSMContext):
    await training_entry(m, state)


@router.message(StateFilter("*"), Command("casting"))
async def sc_casting_cmd(m: Message, state: FSMContext):
    await casting_entry(m, state)


# 🔧 Путь лидера — из любого состояния (без импорта функций из apply.py)
@router.message(StateFilter("*"), Command("apply"))
async def sc_apply_cmd(m: Message, state: FSMContext):
    await state.set_state(ApplyStates.wait_text)
    await m.answer(
        "Путь лидера: короткая заявка.\n\nНапишите, чего хотите достичь — одним сообщением."
    )


# ===== кнопки меню в любом состоянии =====
@router.message(StateFilter("*"), F.text == BTN_TRAIN)
async def sc_training_btn(m: Message, state: FSMContext):
    await training_entry(m, state)


@router.message(StateFilter("*"), F.text == BTN_CASTING)
async def sc_casting_btn(m: Message, state: FSMContext):
    await casting_entry(m, state)


@router.message(StateFilter("*"), F.text == BTN_APPLY)
async def sc_apply_btn(m: Message, state: FSMContext):
    await state.set_state(ApplyStates.wait_text)
    await m.answer(
        "Путь лидера: короткая заявка.\n\nНапишите, чего хотите достичь — одним сообщением."
    )


@router.message(StateFilter("*"), F.text == BTN_PRIVACY)
async def sc_privacy_text(m: Message):
    await m.answer(PRIVACY_TEXT)


@router.message(StateFilter("*"), F.text == BTN_HELP)
async def sc_help_text(m: Message):
    await m.answer(HELP_TEXT)


@router.message(StateFilter("*"), F.text == BTN_PROGRESS)
async def sc_progress_text_exact(m: Message):
    await _send_progress(m)


# «фаззи» подстраховки по текстам (на случай иных эмодзи/пробелов)
@router.message(
    StateFilter("*"),
    lambda m: isinstance(m.text, str) and "прогресс" in m.text.lower(),
)
async def sc_progress_text_fuzzy(m: Message):
    await _send_progress(m)


@router.message(
    StateFilter("*"),
    lambda m: isinstance(m.text, str) and "трениров" in m.text.lower(),
)
async def sc_training_text_fuzzy(m: Message, state: FSMContext):
    await training_entry(m, state)


@router.message(
    StateFilter("*"),
    lambda m: isinstance(m.text, str) and "кастинг" in m.text.lower(),
)
async def sc_casting_text_fuzzy(m: Message, state: FSMContext):
    await casting_entry(m, state)


# ===== Реализация «Мой прогресс» =====
async def _send_progress(m: Message):
    with session_scope() as s:
        u = s.query(User).filter_by(tg_id=m.from_user.id).first()
        if not u:
            await m.answer(
                "Сначала пройди /start, а затем вернись в «Мой прогресс».",
                reply_markup=main_menu(),
            )
            return

        streak = u.streak or 0
        q = s.query(DrillRun).filter(DrillRun.user_id == u.id)

        mapper = sqla_inspect(DrillRun)
        dt_col = next(
            (c for c in mapper.columns if isinstance(c.type, (DateTime, Date))), None
        )

        if dt_col is not None:
            since = datetime.utcnow() - timedelta(days=7)
            runs_7d = q.filter(dt_col >= since).count()
        else:
            runs_7d = q.count()

        # «источник» из meta_json (если есть)
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
        "📈 <b>Мой прогресс</b>\n\n"
        f"• Стрик: <b>{streak}</b>\n"
        f"• Этюдов за 7 дней: <b>{runs_7d}</b>"
        f"{src_txt}\n\n"
        "Продолжай каждый день — тренировка дня в один клик 👇"
    )
    await m.answer(txt, reply_markup=main_menu())
