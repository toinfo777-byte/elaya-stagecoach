# app/routers/leader.py
from __future__ import annotations

import os
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.keyboards.reply import main_menu_kb, BTN_APPLY
from app.storage.repo_extras import save_leader_intent, save_premium_request

router = Router(name="leader")

ADMIN_ALERT_CHAT_ID = int(os.getenv("ADMIN_ALERT_CHAT_ID", "0"))

# ── FSM ───────────────────────────────────────────────────────────────────────
class LeaderStates(StatesGroup):
    intent = State()
    steps = State()     # показываем шаги; ждём «Готово»
    micro = State()     # слово-итог
    premium = State()   # необязательная заявка

# ── Клавиатуры ────────────────────────────────────────────────────────────────
def intent_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="Голос",                 callback_data="leader:intent:voice")
    kb.button(text="Публичные выступления", callback_data="leader:intent:public")
    kb.button(text="Сцена",                 callback_data="leader:intent:stage")
    kb.button(text="Другое",                callback_data="leader:intent:other")
    kb.button(text="🏠 В меню",             callback_data="go:menu")
    kb.adjust(1, 1, 1, 1, 1)
    return kb.as_markup()

def after_steps_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="Готово",    callback_data="leader:done")
    kb.button(text="🏠 В меню", callback_data="go:menu")
    kb.adjust(1, 1)
    return kb.as_markup()

def skip_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="Пропустить", callback_data="leader:skip")
    kb.button(text="🏠 В меню",   callback_data="go:menu")
    kb.adjust(1, 1)
    return kb.as_markup()

# ── Контент шагов ─────────────────────────────────────────────────────────────
def steps_text(intent: str) -> str:
    if intent == "voice":
        return (
            "Голос (3 шага, 2–4 мин)\n\n"
            "1) 30 сек — дыхание «вниз», 2 цикла.\n"
            "2) 60–90 сек — «м-н-з» + фраза дня с 2–3 смысловыми паузами.\n"
            "3) 15 сек — отметь 1 ощущение (слово/эмодзи) и цель «что улучшить».\n\n"
            "Когда закончишь — жми «Готово»."
        )
    if intent == "public":
        return (
            "Публичные выступления (3 шага, 2–4 мин)\n\n"
            "1) 30 сек — фокус на аудитории: сформулируй выгоду слушателя.\n"
            "2) 60–90 сек — схема «тезис → пример → вывод».\n"
            "3) 15 сек — 1 слово-итог + зафиксируй, где ставил паузы.\n\n"
            "Когда закончишь — жми «Готово»."
        )
    if intent == "stage":
        return (
            "Сцена (3 шага, 2–4 мин)\n\n"
            "1) 30 сек — стойка: стопы, колени мягкие, центр внизу.\n"
            "2) 60–90 сек — пройди «маршрут» (3 точки) и скажи текст, останавливаясь в точках для пауз.\n"
            "3) 15 сек — 1 слово-итог (про тело/взгляд/энергию).\n\n"
            "Когда закончишь — жми «Готово»."
        )
    return (
        "Фокус (3 шага, 2–4 мин)\n\n"
        "1) 30 сек — дыхание/стойка.\n"
        "2) 60–90 сек — проговори ключевую мысль с паузами.\n"
        "3) 15 сек — 1 слово-итог.\n\n"
        "Когда закончишь — жми «Готово»."
    )

# ── Старт ─────────────────────────────────────────────────────────────────────
async def _start_leader_core(msg: Message, state: FSMContext):
    await state.set_state(LeaderStates.intent)
    await msg.answer(
        "Путь лидера — твой вектор. 3 шага, 2–4 минуты.\nЧто важнее сейчас?",
        reply_markup=intent_kb(),
    )

@router.message(StateFilter("*"), F.text == BTN_APPLY)
async def start_leader_btn(msg: Message, state: FSMContext):
    await _start_leader_core(msg, state)

@router.message(StateFilter("*"), Command("apply"))
async def start_leader_cmd(msg: Message, state: FSMContext):
    await _start_leader_core(msg, state)

@router.callback_query(StateFilter("*"), F.data == "go:apply")
async def start_leader_cb(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await _start_leader_core(cb.message, state)

# ── Выбор намерения → показываем шаги ─────────────────────────────────────────
@router.callback_query(StateFilter(LeaderStates.intent), F.data.startswith("leader:intent:"))
async def on_intent(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    intent = cb.data.split(":")[-1]
    await state.update_data(intent=intent)
    # первичная запись (без заметки)
    try:
        await save_leader_intent(cb.from_user.id, intent=intent, micro_note=None)
    except Exception:
        pass
    await state.set_state(LeaderStates.steps)
    await cb.message.answer(steps_text(intent), reply_markup=after_steps_kb())

# ── «Готово» после шагов → просим слово-итог ─────────────────────────────────
@router.callback_query(StateFilter(LeaderStates.steps), F.data == "leader:done")
async def on_steps_done(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.set_state(LeaderStates.micro)
    await cb.message.answer(
        "Одним словом: что изменилось? (до 140 символов)",
        reply_markup=skip_kb()
    )

# ── Слово-итог → опциональная заявка или сразу в меню ────────────────────────
@router.message(StateFilter(LeaderStates.micro), F.text)
async def on_micro(msg: Message, state: FSMContext):
    note = (msg.text or "")[:140]
    data = await state.get_data()
    try:
        await save_leader_intent(msg.from_user.id, intent=data["intent"], micro_note=note, upsert=True)
    except Exception:
        pass
    # при желании — шаг с заявкой; оставим краткий поток
    await state.clear()
    await msg.answer("✅ Заявка принята. Мы вернёмся с предложением.", reply_markup=main_menu_kb())

# Скип слова-итога / возврат в меню
@router.callback_query(StateFilter(LeaderStates.micro, LeaderStates.steps, LeaderStates.intent), F.data == "leader:skip")
async def leader_skip(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.clear()
    await cb.message.answer("Ок, вернёмся завтра. Возвращаю в меню.", reply_markup=main_menu_kb())

# универсальный возврат «В меню»
@router.callback_query(StateFilter("*"), F.data == "go:menu")
async def leader_core_menu(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.answer()
    await cb.message.answer("Готово! Открываю меню.", reply_markup=main_menu_kb())

__all__ = ["router"]
