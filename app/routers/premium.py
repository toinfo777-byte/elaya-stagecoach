# app/routers/premium.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from app.keyboards.menu import (
    BTN_PREMIUM,
    main_menu,
)
from app.storage.repo import session_scope
from app.storage.models import User, Lead

router = Router(name="premium")

# --- локальная клавиатура раздела ---
BTN_WHATS_INSIDE = "🔍 Что внутри"
BTN_LEAVE_REQUEST = "📝 Оставить заявку"
BTN_MY_REQUESTS = "📄 Мои заявки"
BTN_BACK_TO_MENU = "📣 В меню"

def premium_kb() -> ReplyKeyboardMarkup:
    rows = [
        [KeyboardButton(text=BTN_WHATS_INSIDE)],
        [KeyboardButton(text=BTN_LEAVE_REQUEST)],
        [KeyboardButton(text=BTN_MY_REQUESTS)],
        [KeyboardButton(text=BTN_BACK_TO_MENU)],
    ]
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True, is_persistent=True)


# --- вход в раздел ---
@router.message(Command("premium"))
@router.message(F.text == BTN_PREMIUM)
async def premium_entry(msg: Message) -> None:
    text = (
        "⭐️ <b>Расширенная версия</b>\n\n"
        "• Ежедневный разбор и обратная связь\n"
        "• Разогрев голоса, дикции и внимания\n"
        "• Мини-кастинг и «путь лидера»\n\n"
        "Выберите действие:"
    )
    await msg.answer(text, reply_markup=premium_kb())


# --- «что внутри» ---
@router.message(F.text == BTN_WHATS_INSIDE)
async def premium_inside(msg: Message) -> None:
    await msg.answer(
        "Внутри расширенной версии — больше практики и персональных разборов.",
        reply_markup=premium_kb(),
    )


# --- «мои заявки» ---
@router.message(F.text == BTN_MY_REQUESTS)
async def premium_my_requests(msg: Message) -> None:
    tg_id = msg.from_user.id
    with session_scope() as s:
        user = s.query(User).filter_by(tg_id=tg_id).first()
        if not user:
            await msg.answer("Заявок пока нет.", reply_markup=premium_kb())
            return

        leads = (
            s.query(Lead)
            .filter(Lead.user_id == user.id, Lead.track == "premium")
            .order_by(Lead.id.desc())
            .all()
        )

    if not leads:
        await msg.answer("Заявок пока нет.", reply_markup=premium_kb())
        return

    lines = ["<b>Мои заявки:</b>"]
    for i, lead in enumerate(leads, 1):
        lines.append(f"• #{i} — {lead.ts:%d.%m %H:%M} — 🟡 новая")
    await msg.answer("\n".join(lines), reply_markup=premium_kb())


# --- «оставить заявку» ---
@router.message(F.text == BTN_LEAVE_REQUEST)
async def premium_leave_request(msg: Message) -> None:
    u = msg.from_user
    with session_scope() as s:
        user = s.query(User).filter_by(tg_id=u.id).first()
        if not user:
            user = User(
                tg_id=u.id,
                username=u.username or None,
                name=(u.full_name or u.first_name or None),
            )
            s.add(user)
            s.flush()

        contact = f"@{u.username}" if u.username else str(u.id)
        lead = Lead(
            user_id=user.id,
            channel="tg",
            contact=contact,
            note=None,
            track="premium",
        )
        s.add(lead)

    await msg.answer("Заявка принята ✅ (без записи в БД).", reply_markup=premium_kb())


# --- «в меню» ---
@router.message(F.text == BTN_BACK_TO_MENU)
async def premium_back_to_menu(msg: Message) -> None:
    await msg.answer("Ок, вернулись в главное меню. Нажми нужную кнопку снизу.", reply_markup=main_menu())
