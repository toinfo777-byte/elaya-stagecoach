from __future__ import annotations

from datetime import datetime, timedelta

from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.types import Message

from sqlalchemy import inspect as sqla_inspect
from sqlalchemy.sql.sqltypes import DateTime, Date

from app.storage.repo import session_scope
from app.storage.models import User, DrillRun
from app.routers.menu import BTN_PROGRESS, main_menu

router = Router(name="progress")

def _progress_text(u: User, runs_7d: int) -> str:
    streak = u.streak or 0
    return (
        "📈 *Мой прогресс*\n\n"
        f"• Стрик: *{streak}*\n"
        f"• Этюдов за 7 дней: *{runs_7d}*\n\n"
        "Продолжай каждый день — тренировка дня в один клик 👇"
    )

@router.message(StateFilter("*"), Command("progress"))
async def cmd_progress(m: Message):
    await send_progress(m)

@router.message(StateFilter("*"), lambda x: x.text == BTN_PROGRESS)
async def btn_progress(m: Message):
    await send_progress(m)

async def send_progress(m: Message):
    with session_scope() as s:
        u = s.query(User).filter_by(tg_id=m.from_user.id).first()
        if not u:
            await m.answer("Сначала пройди /start, а затем вернись в «Мой прогресс».", reply_markup=main_menu())
            return

        q = s.query(DrillRun).filter(DrillRun.user_id == u.id)
        mapper = sqla_inspect(DrillRun)
        dt_col = next((c for c in mapper.columns if isinstance(c.type, (DateTime, Date))), None)

        if dt_col is not None:
            since = datetime.utcnow() - timedelta(days=7)
            runs_7d = q.filter(dt_col >= since).count()
        else:
            runs_7d = q.count()

    await m.answer(_progress_text(u, runs_7d), parse_mode="Markdown", reply_markup=main_menu())
