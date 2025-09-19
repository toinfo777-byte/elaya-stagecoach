from __future__ import annotations

from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from aiogram.utils.keyboard import InlineKeyboardBuilder

from sqlalchemy import text

from app.keyboards.menu import (
    BTN_PREMIUM,
)
from app.storage.repo import SessionLocal

router = Router(name="premium")


# --------- FSM ---------
class PremiumForm(StatesGroup):
    waiting_goal = State()


# --------- inline-клавиатуры ---------
def kb_premium_menu() -> types.InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Что внутри", callback_data="prem:inside")
    kb.button(text="Оставить заявку", callback_data="prem:req")
    kb.button(text="Мои заявки", callback_data="prem:list")
    kb.button(text="📣 В меню", callback_data="prem:menu")
    kb.adjust(2, 2)
    return kb.as_markup()

# --------- утилиты ---------
def _markdown_premium_intro() -> str:
    return (
        "⭐️ <b>Расширенная версия</b>\n\n"
        "• Ежедневный разбор и обратная связь\n"
        "• Разогрев голоса, дикции и внимания\n"
        "• Мини-кастинг и путь лидера\n\n"
        "<i>Выберите действие:</i>"
    )


def _ensure_user_and_get_id(telegram_id: int, username: str | None) -> int:
    """Возвращает id нашего пользователя (создаёт пустого при необходимости)."""
    with SessionLocal() as s:
        row = s.execute(
            text("SELECT id FROM users WHERE tg_id = :tg"),
            {"tg": telegram_id},
        ).fetchone()
        if row:
            return int(row[0])

        s.execute(
            text(
                "INSERT INTO users (tg_id, username, streak) VALUES (:tg, :un, 0)"
            ),
            {"tg": telegram_id, "un": username or None},
        )
        s.commit()
        row = s.execute(
            text("SELECT id FROM users WHERE tg_id = :tg"),
            {"tg": telegram_id},
        ).fetchone()
        return int(row[0])


async def _show_premium_menu(message: types.Message) -> None:
    await message.answer(_markdown_premium_intro(), reply_markup=kb_premium_menu())


# --------- вход в раздел ---------
@router.message(Command("premium"))
@router.message(F.text == BTN_PREMIUM, state="*")
async def premium_entry(message: types.Message, state: FSMContext) -> None:
    # «супер-кнопка»: чистим любое состояние и открываем раздел
    await state.clear()
    await _show_premium_menu(message)


# --------- Что внутри ---------
@router.callback_query(F.data == "prem:inside", state="*")
async def prem_inside(cb: types.CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await cb.message.answer(
        "Внутри — разбор ваших ответов и аудио, ежедневные микро-тренировки и обратная связь.\n"
        "Если хотите попробовать — нажмите «Оставить заявку».",
        reply_markup=kb_premium_menu(),
    )
    await cb.answer()


# --------- Оставить заявку (старт) ---------
@router.callback_query(F.data == "prem:req", state="*")
async def prem_request_start(cb: types.CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(PremiumForm.waiting_goal)
    await cb.message.answer(
        "Путь лидера: короткая заявка.\n"
        "Напишите, чего хотите достичь — одним сообщением (до 200 символов).\n"
        "Если передумали — отправьте /cancel.",
    )
    await cb.answer()


# отмена
@router.message(Command("cancel"), PremiumForm.waiting_goal)
async def prem_cancel(message: types.Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Ок, вернулись в главное меню. Нажми нужную кнопку снизу.")
    # возвращаем меню раздела, чтобы было куда вернуться сразу
    await _show_premium_menu(message)


# --------- Оставить заявку (приём текста) ---------
@router.message(PremiumForm.waiting_goal)
async def prem_request_save(message: types.Message, state: FSMContext) -> None:
    user_id = _ensure_user_and_get_id(
        message.from_user.id,
        getattr(message.from_user, "username", None),
    )
    goal_text = (message.text or "").strip()[:200]

    # Пишем в premium_requests
    with SessionLocal() as s:
        # для sqlite JSON — обычная строка '{}' (без ::jsonb)
        s.execute(
            text(
                "INSERT INTO premium_requests (user_id, tg_username, status, meta) "
                "VALUES (:uid, :un, 'new', :meta)"
            ),
            {
                "uid": user_id,
                "un": getattr(message.from_user, "username", None),
                "meta": "{}",
            },
        )
        s.commit()

    await state.clear()
    await message.answer("Спасибо! Принял. Двигаемся дальше 👍")
    await _show_premium_menu(message)


# --------- Мои заявки ---------
@router.callback_query(F.data == "prem:list", state="*")
async def prem_list(cb: types.CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    user_id = _ensure_user_and_get_id(cb.from_user.id, getattr(cb.from_user, "username", None))

    with SessionLocal() as s:
        rows = s.execute(
            text(
                "SELECT id, created_at, status "
                "FROM premium_requests WHERE user_id = :uid "
                "ORDER BY id DESC LIMIT 5"
            ),
            {"uid": user_id},
        ).fetchall()

    if not rows:
        await cb.message.answer("Заявок пока нет.", reply_markup=kb_premium_menu())
        await cb.answer()
        return

    status_emoji = {"new": "🟡", "in_review": "🟠", "done": "🟢"}
    lines = []
    for rid, created_at, status in rows:
        mark = status_emoji.get(status, "⚪️")
        ts = str(created_at)[:16] if created_at else ""
        lines.append(f"• #{rid} — {ts} — {mark} {status}")

    await cb.message.answer(
        "<b>Мои заявки:</b>\n" + "\n".join(lines),
        reply_markup=kb_premium_menu(),
    )
    await cb.answer()


# --------- «В меню» внутри раздела ---------
@router.callback_query(F.data == "prem:menu", state="*")
async def prem_back_to_menu(cb: types.CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await cb.message.answer("Ок, вернулись в главное меню. Нажми нужную кнопку снизу.")
    await cb.answer()
