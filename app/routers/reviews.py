# app/routers/reviews.py
from __future__ import annotations

import logging
from textwrap import dedent

from aiogram import Router, F
from aiogram.types import Message, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from app.keyboards.main_menu import MAIN_MENU
from app.config import settings

router = Router(name="reviews-router")

# --- состояния FSM -----

class ReviewState(StatesGroup):
    waiting_text = State()


# --- утилита: отправить отзыв админу / в лог -----

async def _send_review_to_admin(bot: Bot, user: Message.from_user.__class__, emoji: str, text: str) -> None:
    """
    Отправляем отзыв в админ-чат (если задан), плюс пишем в лог.
    """
    uid = user.id if user else "unknown"
    uname = f"@{user.username}" if getattr(user, "username", None) else ""
    full_name = f"{user.full_name}" if getattr(user, "full_name", None) else ""

    body = dedent(
        f"""
        🌕 <b>Новый отзыв тренеру</b>
        • Пользователь: <code>{uid}</code> {uname} {full_name}
        • Оценка: {emoji}
        • Текст: {text.strip() or "—"}
        """
    ).strip()

    logging.info("review: uid=%s emoji=%s text=%r", uid, emoji, text)

    chat_id = settings.admin_alert_chat_id
    if chat_id:
        try:
            await bot.send_message(chat_id, body)
        except Exception as e:  # логируем, но не падаем
            logging.warning("failed to send review to admin: %s", e)


# --- 1) короткий путь: эмодзи + текст в одном сообщении -----

@router.message(
    F.text.regexp(r"^(⭐|👍|🔥|💡).+")
)
async def handle_review_inline(message: Message, bot: Bot) -> None:
    """
    Backward-compatible: пользователь отправляет эмодзи + короткий текст
    в одном сообщении, как раньше: «⭐ Очень крутой бот».

    Мы:
    — парсим первый символ как «оценку»;
    — принимаем всё остальное как текст;
    — сохраняем отзыв и возвращаем в главное меню.
    """
    text = message.text or ""
    emoji = text[0]
    review_text = text[1:].strip()

    await _send_review_to_admin(bot, message.from_user, emoji, review_text)

    await message.answer(
        "Спасибо за отзыв! Я учту это в дальнейшем развитии Элайи 🌕",
        reply_markup=MAIN_MENU,
    )


# --- 2) основной путь: сначала эмодзи, потом фраза -----

@router.message(
    F.text.regexp(r"^(⭐|👍|🔥|💡)$")
)
async def start_review_flow(message: Message, state: FSMContext) -> None:
    """
    Основной сценарий:
    1) пользователь отправляет только эмодзи (оценку);
    2) мы просим одну короткую фразу;
    3) потом фиксируем отзыв и возвращаем в главное меню.
    """
    emoji = (message.text or "").strip()
    await state.update_data(emoji=emoji)

    await message.answer(
        "Спасибо! Теперь в одной короткой фразе напиши, "
        "что именно тебе понравилось или не понравилось.",
    )
    await state.set_state(ReviewState.waiting_text)


@router.message(ReviewState.waiting_text, F.text)
async def finish_review_flow(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Пользователь прислал текст после эмодзи.
    Завершаем сценарий, отправляем отзыв админам и возвращаем в меню.
    """
    data = await state.get_data()
    emoji = data.get("emoji", "⭐")
    review_text = message.text or ""

    await _send_review_to_admin(bot, message.from_user, emoji, review_text)

    await message.answer(
        "Спасибо за отзыв! Я записал его и учту в развитии Элайи 🌕",
        reply_markup=MAIN_MENU,
    )
    await state.clear()
