# app/routers/premium.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from sqlalchemy import select, desc

from app.config import settings
from app.storage.repo import session_scope
from app.storage.models import User
from app.utils.dt import fmt_local

# Если у вас модель premium_requests лежит в другом модуле — поправьте import:
from app.storage.models import PremiumRequest  # id, user_id, created_at, status, meta

router = Router(name="premium")

# --- Клавиатуры --------------------------------------------------------------

KB_PREMIUM = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Что внутри"), KeyboardButton(text="Оставить заявку")],
        [KeyboardButton(text="Мои заявки"), KeyboardButton(text="🏠 В меню")],
    ],
    resize_keyboard=True,
)

# --- Helpers -----------------------------------------------------------------

STATUS_EMOJI = {
    "new": "🟡",
    "seen": "🟠",
    "approved": "🟢",
    "rejected": "🔴",
}


def _status_badge(status: str) -> str:
    return f"{STATUS_EMOJI.get(status, '🟡')} {status}"


async def _render_my_requests(user: User) -> str:
    with session_scope() as s:
        rows = s.execute(
            select(PremiumRequest).where(PremiumRequest.user_id == user.id).order_by(desc(PremiumRequest.created_at))
        ).scalars().all()

    if not rows:
        return "Заявок пока нет."

    lines = ["Мои заявки:"]
    for i, r in enumerate(rows, start=1):
        when = fmt_local(r.created_at, user.tz, settings.TZ_DEFAULT)
        lines.append(f"• #{i} — {when} — {_status_badge(r.status)}")
    return "\n".join(lines)


# --- Handlers ----------------------------------------------------------------

@router.message(F.text == "⭐️ Расширенная версия")
@router.message(F.text == "/premium")
async def on_premium_menu(m: Message, user: User):
    await m.answer("⭐️ Расширенная версия", reply_markup=KB_PREMIUM)


@router.message(F.text == "Что внутри")
async def on_premium_inside(m: Message, user: User):
    await m.answer(
        "В расширенной версии — персональные тренировки, обратная связь и живые разборы.\n\n"
        "Оставьте заявку — и мы подключим вас, когда будет слот.",
        reply_markup=KB_PREMIUM,
    )


@router.message(F.text == "Оставить заявку")
async def on_premium_apply(m: Message, user: User):
    with session_scope() as s:
        s.add(PremiumRequest(user_id=user.id, status="new", meta={}))
    await m.answer("Заявка принята ✅ (без записи в БД)", reply_markup=KB_PREMIUM)
    # ↑ текст сохранён из вашего UX; при необходимости замените


@router.message(F.text == "Мои заявки")
async def on_premium_list(m: Message, user: User):
    text = await _render_my_requests(user)
    await m.answer(text, reply_markup=KB_PREMIUM)


@router.message(F.text == "🏠 В меню")
async def on_back_to_menu(m: Message, user: User):
    from app.keyboards.menu import main_menu
    await m.answer("Ок, вернулись в главное меню. Нажми нужную кнопку снизу.", reply_markup=main_menu())
