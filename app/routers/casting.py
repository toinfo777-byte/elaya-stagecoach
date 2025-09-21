from __future__ import annotations

import json
from typing import List, Dict, Any

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from app.config import settings
from app.keyboards.menu import main_menu, BTN_CASTING
from app.storage.mvp_repo import save_casting_application

router = Router(name="casting")

# Вопросы MVP (можно потом подменить на YAML)
QUESTIONS: List[Dict[str, Any]] = [
    {"key": "name",       "label": "Как тебя зовут?",         "type": "text",   "required": True,  "hint": "Имя и фамилия"},
    {"key": "age",        "label": "Сколько тебе лет?",       "type": "number", "required": True,  "min": 10, "max": 99},
    {"key": "city",       "label": "Из какого ты города?",    "type": "text",   "required": True},
    {"key": "experience", "label": "Какой у тебя опыт?",      "type": "choice", "required": True,  "options": ["нет", "1–2 года", "3+ лет"]},
    {"key": "contact",    "label": "Контакт для связи",       "type": "text",   "required": True,  "hint": "@username / телефон / email"},
    {"key": "portfolio",  "label": "Ссылка на портфолио (если есть)", "type": "url", "required": False},
]

def kb_choices(options: List[str]) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=o)] for o in options],
        resize_keyboard=True
    )

class CastingSG(StatesGroup):
    q = State()


@router.message(F.text == BTN_CASTING)
@router.message(Command("casting"))
async def casting_entry(m: Message, state: FSMContext) -> None:
    await state.clear()
    await state.update_data(idx=0, answers={})
    await ask_next(m, state)


@router.message(Command("apply"))
async def apply_entry(m: Message, state: FSMContext) -> None:
    # По ТЗ: «Путь лидера» может дублировать кастинг — так и сделаем в MVP
    await casting_entry(m, state)


async def ask_next(m: Message, state: FSMContext) -> None:
    data = await state.get_data()
    idx = int(data.get("idx", 0))
    if idx >= len(QUESTIONS):
        await finish_form(m, state)
        return

    q = QUESTIONS[idx]
    hint = f"\n<i>{q.get('hint','')}</i>" if q.get("hint") else ""

    # Если choice — даём клавиатуру с вариантами
    if q["type"] == "choice":
        await m.answer(f"{q['label']}{hint}", reply_markup=kb_choices(q["options"]))
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

    # простая валидация
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
        if text and not (text.startswith("http://") or text.startswith("https://")):
            await m.reply("Нужно прислать ссылку (http/https) или оставить пустым.")
            return
        answers[q["key"]] = text
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


async def finish_form(m: Message, state: FSMContext) -> None:
    data = await state.get_data()
    answers = data.get("answers", {})
    await state.clear()

    # Сохраним в БД
    app_id = save_casting_application(m.from_user.id, json.dumps(answers, ensure_ascii=False))

    # Уведомим админа (если настроен)
    if settings.admin_alert_chat_id:
        lines = [
            "🎬 <b>Новая заявка (мини-кастинг)</b>",
            f"• ID: {app_id}",
            f"• Пользователь: @{m.from_user.username or '—'} (id {m.from_user.id})",
        ]
        for q in QUESTIONS:
            k, label = q["key"], q["label"]
            v = answers.get(k, "—")
            lines.append(f"• {label}: {v}")
        await m.bot.send_message(settings.admin_alert_chat_id, "\n".join(lines))

    await m.answer(
        "Заявка принята! Мы свяжемся в течение 1–2 дней. 🌟",
        reply_markup=main_menu()
    )
