# app/routers/premium.py
from __future__ import annotations

import os
from datetime import datetime

from aiogram import Router, F, types
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.storage.repo import add_premium_request, list_user_premium_requests
from app.keyboards.menu import (
    BTN_PREMIUM,
    BTN_TRAIN, BTN_PROGRESS, BTN_APPLY, BTN_CASTING, BTN_PRIVACY, BTN_HELP, BTN_SETTINGS,
    main_menu,
)

router = Router(name="premium")

# --- callback data ---
CB_APPLY = "premium:apply"
CB_LIST = "premium:list"
CB_INFO = "premium:info"
CB_BACK = "premium:back"

ADMIN_ALERT_CHAT_ID = os.getenv("ADMIN_ALERT_CHAT_ID")  # опционально


def premium_kb() -> types.InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Что внутри", callback_data=CB_INFO)
    kb.button(text="Оставить заявку", callback_data=CB_APPLY)
    kb.button(text="Мои заявки", callback_data=CB_LIST)
    kb.button(text="⬅️ В меню", callback_data=CB_BACK)
    kb.adjust(2, 2)
    return kb.as_markup()


def _format_status(status: str) -> str:
    mapping = {
        "new": "🟡 новая",
        "in_review": "🟠 в рассмотрении",
        "approved": "🟢 одобрено",
        "rejected": "🔴 отклонено",
    }
    return mapping.get(status, status)


@router.message(F.text == BTN_PREMIUM)
async def premium_entry(msg: Message) -> None:
    await msg.answer(
        "⭐ Расширенная версия\n\n"
        "Здесь можно оставить заявку на расширенные возможности тренинга.",
        reply_markup=premium_kb(),
    )


@router.callback_query(F.data == CB_BACK)
async def premium_back(cb: CallbackQuery) -> None:
    await cb.message.edit_text("Ок, вернёмся в главное меню. Нужная кнопка снизу 👇")
    await cb.message.answer("Меню:", reply_markup=main_menu())
    await cb.answer()


@router.callback_query(F.data == CB_INFO)
async def premium_info(cb: CallbackQuery) -> None:
    await cb.message.edit_text(
        "Что внутри расширенной версии:\n"
        "• персональные разборы и обратная связь;\n"
        "• расширенная аналитика прогресса;\n"
        "• уведомления и план тренировок.\n\n"
        "Готовы попробовать? Нажмите «Оставить заявку».",
        reply_markup=premium_kb(),
    )
    await cb.answer()


@router.callback_query(F.data == CB_APPLY)
async def premium_apply(cb: CallbackQuery) -> None:
    user = cb.from_user
    pr = add_premium_request(user.id, user.username)

    # алерт админу (если указан)
    if ADMIN_ALERT_CHAT_ID:
        try:
            await cb.bot.send_message(
                int(ADMIN_ALERT_CHAT_ID),
                f"🆕 Заявка на ⭐ Премиум\n"
                f"user_id: <code>{user.id}</code>\n"
                f"@{user.username or '—'}\n"
                f"status: {pr.status}\n"
                f"id: {pr.id}",
            )
        except Exception:
            pass

    text = (
        "Заявка принята ✅\n\n"
        "Мы свяжемся с вами или включим доступ автоматически.\n"
        "Статус можно смотреть в «Мои заявки»."
    )
    await cb.message.edit_text(text, reply_markup=premium_kb())
    await cb.answer("Заявка отправлена")


@router.callback_query(F.data == CB_LIST)
async def premium_list(cb: CallbackQuery) -> None:
    rows = list_user_premium_requests(cb.from_user.id, limit=10)

    if not rows:
        await cb.message.edit_text("Заявок пока нет.", reply_markup=premium_kb())
        await cb.answer()
        return

    lines = []
    for r in rows:
        created = r.created_at
        if isinstance(created, str):
            try:
                created = datetime.fromisoformat(created)
            except Exception:
                created = None
        dt = created.strftime("%d.%m %H:%M") if isinstance(created, datetime) else "—"
        lines.append(f"• #{r.id} — {dt} — {_format_status(r.status)}")

    await cb.message.edit_text("Мои заявки:\n" + "\n".join(lines), reply_markup=premium_kb())
    await cb.answer()
