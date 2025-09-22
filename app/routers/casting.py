# app/routers/casting.py
from __future__ import annotations

import re
from typing import List, Dict, Any

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)

from app.keyboards.menu import main_menu, BTN_CASTING
from app.storage.repo import save_casting
from app.utils.admin import notify_admin  # 👈 используем helper

router = Router(name="casting")

# Вопросы MVP
QUESTIONS: List[Dict[str, Any]] = [
    {"key": "name",       "label": "Как тебя зовут?",         "type": "text",   "required": True,  "hint": "Имя и фамилия"},
    {"key": "age",        "label": "Сколько тебе лет?",       "type": "number", "required": True,  "min": 10, "max": 99},
    {"key": "city",       "label": "Из какого ты города?",    "type": "text",   "required": True},
    {"key": "experience", "label": "Какой у тебя опыт?",      "type": "choice", "required": True,  "options": ["нет", "1–2 года", "3+ лет"]},
    {"key": "contact",    "label": "Контакт для связи",       "type": "text",   "required": True,  "hint": "@username / телефон / email"},
    {"key": "portfolio",  "label": "Ссылка на портфолио (если есть)", "type": "url", "required": False},
]

URL_RE = re.compile(r"^https?://", re.I)
BTN_SKIP = "Пропустить"

SUCCESS_TEXT = (
    "✅ Заявка принята! Мы свяжемся в течение 1–2 дней.\n"
    "Спасибо, что уделил(а) время. Возвращайся к тренировкам!"
)


def kb_choices(options: List[str]) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=o)] for o in options],
        resize_keyboard=True
    )


def optional_url_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=BTN_SKIP, callback_data="cast:skip_url")]
    ])


class CastingSG(StatesGroup):
    q = State()


# ==== Старт ====
@router.message(F.text == BTN_CASTING)
@router.message(Command("casting"))
async def casting_entry(m: Message, state: FSMContext) -> None:
    await start_casting_flow(m, state)


@router.message(Command("apply"))
async def apply_entry(m: Message, state: FSMContext) -> None:
    # «Путь лидера» = алиас на мини-кастинг
    await start_casting_flow(m, state)


async def start_casting_flow(message: Message, state: FSMContext):
    """Публичная точка входа (используется диплинком)."""
    await state.clear()
    await state.update_data(idx=0, answers={})
    await ask_next(message, state)


# ==== Диалог ====
async def ask_next(m: Message, state: FSMContext) -> None:
    data = await state.get_data()
    idx = int(data.get("idx", 0))
    if idx >= len(QUESTIONS):
        await finish_casting(m, state)
        return

    q = QUESTIONS[idx]
    hint = f"\n<i>{q.get('hint','')}</i>" if q.get("hint") else ""

    if q["type"] == "choice":
        await m.answer(f"{q['label']}{hint}", reply_markup=kb_choices(q["options"]))
    elif q["type"] == "url" and not q.get("required", False):
        await m.answer(f"{q['label']}{hint}", reply_markup=optional_url_kb())
    else:
        await m.answer(f"{q['label']}{hint}")

    await state.set_state(CastingSG.q)


@router.message(CastingSG.q)
async def collect_answer(m: Message, state: FSMContext) -> None:
    data = await state.get_data()
    idx = int(data.get("idx", 0))
    answers = dict(data.get("answers", {}))
    q = QUESTIONS[idx]

    text = (m.text or "").strip()

    # Валидация
    if q["type"] == "number":
        if not text.isdigit():
            await m.reply("Введите число.")
            return
        val = int(text)
        if ("min" in q and val < q["min"]) or ("max" in q and val > q["max"]):
            await m.reply(f"Допустимый диапазон: {q.get('min','?')}–{q.get('max','?')}.")
            return
        answers[q["key"]] = val

    elif q["type"] == "url":
        if not text or text.lower() in {"нет", "пусто", "no", "-"}:
            answers[q["key"]] = None
        elif URL_RE.match(text):
            answers[q["key"]] = text
        else:
            await m.answer("Нужно прислать ссылку (http/https) или нажми «Пропустить».",
                           reply_markup=optional_url_kb())
            return

    elif q["type"] == "choice":
        opts = set(q["options"])
        if text not in opts:
            await m.reply("Выберите вариант кнопкой ниже.")
            return
        answers[q["key"]] = text

    else:
        if q.get("required") and not text:
            await m.reply("Поле обязательно.")
            return
        answers[q["key"]] = text

    # Следующий вопрос
    idx += 1
    await state.update_data(idx=idx, answers=answers)
    await ask_next(m, state)


# ==== Callback: Пропуск URL ====
@router.callback_query(F.data == "cast:skip_url")
async def casting_skip_url(c: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    idx = int(data.get("idx", 0))
    if 0 <= idx < len(QUESTIONS) and QUESTIONS[idx]["key"] == "portfolio":
        answers = dict(data.get("answers", {}))
        answers["portfolio"] = None
        try:
            await c.message.edit_reply_markup(reply_markup=None)
        except Exception:
            pass
        idx += 1
        await state.update_data(idx=idx, answers=answers)
        await ask_next(c.message, state)
    await c.answer()


# ==== Финиш ====
async def finish_casting(message: Message, state: FSMContext):
    data = await state.get_data()
    answers = data.get("answers", {}) or {}
    await state.clear()

    # Сохраняем в БД
    await save_casting(
        tg_id=message.from_user.id,
        name=str(answers.get("name", "")),
        age=int(answers.get("age", 0) or 0),
        city=str(answers.get("city", "")),
        experience=str(answers.get("experience", "")),
        contact=str(answers.get("contact", "")),
        portfolio=answers.get("portfolio"),
        agree_contact=True,
    )

    # Алерт админу (helper)
    lines = [
        "🎬 Новая заявка (мини-кастинг):",
        f"• Пользователь: @{message.from_user.username or '—'} (id {message.from_user.id})",
    ]
    for q in QUESTIONS:
        k, label = q["key"], q["label"]
        v = answers.get(k, "—")
        lines.append(f"• {label}: {v}")
    await notify_admin(message.bot, "\n".join(lines))

    # Экран «заявка принята»
    await message.answer(SUCCESS_TEXT, reply_markup=main_menu())
