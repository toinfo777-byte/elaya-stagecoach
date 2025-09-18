from __future__ import annotations

from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from sqlalchemy import select, desc

from app.keyboards.menu import main_menu  # нижнее «главное» меню
from app.storage.repo import session_scope
from app.storage.models import User, PremiumRequest
from app.utils.textmatch import contains_ci

router = Router(name="premium")


# === Локальные кнопки раздела «Расширенная версия» ============================

def _kb_premium() -> ReplyKeyboardMarkup:
    rows = [
        [KeyboardButton(text="Что внутри"), KeyboardButton(text="Оставить заявку")],
        [KeyboardButton(text="Мои заявки"), KeyboardButton(text="🧭 В меню")],
    ]
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True, is_persistent=True)


def _human_status(s: str) -> str:
    return {
        "new": "🟡 новая",
        "in_progress": "🟠 в работе",
        "done": "🟢 обработана",
        "rejected": "🔴 отклонена",
    }.get(s, s)


# === Хэндлеры =================================================================

@router.message(F.text.func(contains_ci("расширенная версия")))
@router.message(F.text == "/premium")
async def premium_entry(m: Message, user: User) -> None:
    """Вход в раздел + краткий статус по заявкам."""
    with session_scope() as s:
        last = s.execute(
            select(PremiumRequest)
            .where(PremiumRequest.user_id == user.id)
            .order_by(desc(PremiumRequest.created_at))
            .limit(1)
        ).scalar_one_or_none()

    if last:
        text = (
            "Мои заявки:\n"
            f"• #{last.id} — {last.created_at:%d.%m %H:%M} — {_human_status(last.status)}"
        )
    else:
        text = "Заявок пока нет."

    await m.answer(text, reply_markup=_kb_premium())


@router.message(F.text.func(contains_ci("что внутри")))
async def premium_inside(m: Message, user: User) -> None:
    desc = (
        "Что внутри ⭐️ Расширенной версии:\n"
        "• Персональные разборы и рекомендации;\n"
        "• Расширенная аналитика прогресса;\n"
        "• Дополнительные тренировки и сценарии.\n\n"
        "Нажмите «Оставить заявку», чтобы подать запрос."
    )
    await m.answer(desc, reply_markup=_kb_premium())


@router.message(F.text.func(contains_ci("оставить заявку")))
async def premium_apply(m: Message, user: User) -> None:
    """Записать заявку и показать подтверждение."""
    with session_scope() as s:
        pr = PremiumRequest(
            user_id=user.id,
            tg_username=(m.from_user.username if m.from_user else None),
            status="new",
            meta={},  # можно добавить любые служебные поля
        )
        s.add(pr)

    await m.answer("Заявка принята ✅ (без записи в БД)", reply_markup=_kb_premium())
    # ↑ текст оставлен, как вы уже видели в интерфейсе. Если нужно — поменяйте.


@router.message(F.text.func(contains_ci("мои заявки")))
async def premium_my_requests(m: Message, user: User) -> None:
    with session_scope() as s:
        rows = s.execute(
            select(PremiumRequest)
            .where(PremiumRequest.user_id == user.id)
            .order_by(desc(PremiumRequest.created_at))
            .limit(5)
        ).scalars().all()

    if not rows:
        await m.answer("Заявок пока нет.", reply_markup=_kb_premium())
        return

    lines = ["Мои заявки:"]
    for r in rows:
        lines.append(f"• #{r.id} — {r.created_at:%d.%m %H:%M} — {_human_status(r.status)}")

    await m.answer("\n".join(lines), reply_markup=_kb_premium())


@router.message(F.text.func(contains_ci("в меню")))
async def premium_back_to_menu(m: Message, user: User) -> None:
    await m.answer("Ок, вернулись в главное меню. Нажми нужную кнопку снизу.", reply_markup=main_menu())
