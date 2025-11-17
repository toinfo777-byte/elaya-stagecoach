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


class ReviewState(StatesGroup):
    waiting_text = State()


EMOJIS = ("⭐", "👍", "🔥", "💡")


async def _send_review_to_admin(bot: Bot, message: Message, emoji: str, text: str) -> None:
    """Отправляем отзыв в лог и, при наличии ADMIN_ALERT_CHAT_ID, в админ-чат."""
    user = message.from_user
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
        except Exception as e:
            logging.warning("failed to send review to admin: %s", e)


@router.message(
    F.text.regexp(r"^⭐|^👍|^🔥|^💡"),  # как в старой версии, которая работала
    ~ReviewState.waiting_text,        # только если мы не ждём текст
)
async def start_or_inline_review(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Универсальный вход в отзывы.

    Если пользователь отправил:
    • «⭐ Очень крутой бот» — сразу принимаем отзыв;
    • «⭐» — просим одну короткую фразу и включаем FSM.
    """
    text = (message.text or "").strip()
    if not text:
        return

    emoji = text[0]
    if emoji not in EMOJIS:
        return

    rest = text[1:].strip()

    if rest:
        # старый режим: эмодзи + фраза в одном сообщении
        await _send_review_to_admin(bot, message, emoji, rest)
        await message.answer(
            "Спасибо за отзыв! Я учту это в дальнейшем развитии Элайи 🌕",
            reply_markup=MAIN_MENU,
        )
        return

    # новый режим: только эмодзи → просим фразу
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
    Завершаем сценарий, отправляем отзыв и возвращаем в меню.
    """
    data = await state.get_data()
    emoji = data.get("emoji", "⭐")
    review_text = message.text or ""

    await _send_review_to_admin(bot, message, emoji, review_text)

    await message.answer(
        "Спасибо за отзыв! Я записал его и учту в развитии Элайи 🌕",
        reply_markup=MAIN_MENU,
    )
    await state.clear()
