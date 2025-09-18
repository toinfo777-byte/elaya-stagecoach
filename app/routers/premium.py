# app/routers/premium.py
from __future__ import annotations

import os
import json
import logging
from datetime import datetime

from aiogram import Router, F, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Пытаемся импортировать БД, но не рушим бота если её нет
try:
    from app.storage.repo import SessionLocal  # sync Session
    from sqlalchemy import text
except Exception:  # pragma: no cover
    SessionLocal = None  # type: ignore
    text = None  # type: ignore

log = logging.getLogger(__name__)
router = Router()

PREMIUM_BTN_TEXT = "⭐️ Расширенная версия"


def _kb_main() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(
        InlineKeyboardButton(text="Что внутри", callback_data="prem:info"),
        InlineKeyboardButton(text="Оставить заявку", callback_data="prem:apply"),
    )
    kb.row(
        InlineKeyboardButton(text="Мои заявки", callback_data="prem:myreq"),
        InlineKeyboardButton(text="⬅️ В меню", callback_data="prem:back"),
    )
    return kb.as_markup()


@router.message(F.text == PREMIUM_BTN_TEXT)
async def premium_entry(msg: types.Message) -> None:
    await msg.answer(
        "⭐️ Расширенная версия\n\n"
        "Дополнительные тренировки, расширенная аналитика, поддержка и бонус-материалы.",
        reply_markup=_kb_main(),
    )


@router.callback_query(F.data == "prem:back")
async def premium_back(cb: types.CallbackQuery) -> None:
    await cb.message.edit_text("Ок, вернулись в главное меню. Нажми нужную кнопку снизу.")
    await cb.answer()


@router.callback_query(F.data == "prem:info")
async def premium_info(cb: types.CallbackQuery) -> None:
    await cb.message.edit_text(
        "Что внутри ⭐️:\n"
        "• Ежедневные расширенные тренировки\n"
        "• Отчёт по прогрессу и источникам трафика\n"
        "• Поддержка и рекомендации\n\n"
        "Нажми «Оставить заявку», если хочешь доступ.",
        reply_markup=_kb_main(),
    )
    await cb.answer()


# ---------- Заявка на премиум ----------

def _db_available() -> bool:
    return bool(SessionLocal and text)


def _insert_request_sync(user_id: int, username: str | None) -> None:
    """
    Пишем в таблицу premium_requests. Таблица создана миграцией.
    Для SQLite/PG работает одинаково (без jsonb-спецсинтаксиса).
    """
    assert SessionLocal and text  # для type checkers
    with SessionLocal() as s:
        s.execute(
            text(
                """
                INSERT INTO premium_requests (id, user_id, tg_username, created_at, status, meta)
                VALUES (:id, :user_id, :tg, :dt, :st, :meta)
                """
            ),
            {
                "id": int(datetime.utcnow().timestamp() * 1000),  # простой уникальный id
                "user_id": user_id,
                "tg": username or "",
                "dt": datetime.utcnow(),
                "st": "new",
                "meta": json.dumps({}),
            },
        )
        s.commit()


def _get_user_requests_sync(user_id: int) -> list[tuple]:
    assert SessionLocal and text
    with SessionLocal() as s:
        rows = s.execute(
            text(
                """
                SELECT id, created_at, status
                FROM premium_requests
                WHERE user_id = :uid
                ORDER BY created_at DESC
                LIMIT 10
                """
            ),
            {"uid": user_id},
        ).fetchall()
    return rows


def _admin_chat_id() -> int | None:
    # Берём из ENV, если задан
    val = os.getenv("ADMIN_ALERT_CHAT_ID") or os.getenv("ADMIN_CHAT_ID")
    try:
        return int(val) if val else None
    except Exception:
        return None


@router.callback_query(F.data == "prem:apply")
async def premium_apply(cb: types.CallbackQuery) -> None:
    # Пишем заявку, если доступна БД. Иначе — просто уведомляем.
    if _db_available():
        try:
            _insert_request_sync(cb.from_user.id, cb.from_user.username)
            status = "Заявка отправлена ✅"
        except Exception as e:  # не роняем UX
            log.exception("premium request insert failed: %s", e)
            status = "Заявка принята ✅ (без записи в БД)"
    else:
        status = "Заявка принята ✅"

    # Уведомление админу (если указан)
    admin_id = _admin_chat_id()
    if admin_id:
        try:
            await cb.message.bot.send_message(
                admin_id,
                (
                    "🔔 Новая заявка на ⭐️ Расширенную версию\n"
                    f"user_id: <code>{cb.from_user.id}</code>\n"
                    f"username: @{cb.from_user.username or '—'}"
                ),
            )
        except Exception as e:
            log.warning("admin notify failed: %s", e)

    await cb.message.edit_text(
        f"{status}\n\nМы свяжемся с тобой или включим доступ автоматически.",
        reply_markup=_kb_main(),
    )
    await cb.answer("Заявка отправлена")


@router.callback_query(F.data == "prem:myreq")
async def premium_my_requests(cb: types.CallbackQuery) -> None:
    if not _db_available():
        await cb.message.edit_text(
            "Пока не могу показать заявки (БД недоступна). Попробуй позже.",
            reply_markup=_kb_main(),
        )
        await cb.answer()
        return

    try:
        rows = _get_user_requests_sync(cb.from_user.id)
    except Exception as e:
        log.exception("select premium requests failed: %s", e)
        rows = []

    if not rows:
        text = "Заявок пока нет."
    else:
        items = []
        for r in rows:
            _id, created_at, status = r
            dt = (
                created_at.strftime("%d.%m %H:%M")
                if hasattr(created_at, "strftime")
                else str(created_at)
            )
            items.append(f"• #{_id} — {status} ({dt})")
        text = "Твои заявки:\n" + "\n".join(items)

    await cb.message.edit_text(text, reply_markup=_kb_main())
    await cb.answer()
