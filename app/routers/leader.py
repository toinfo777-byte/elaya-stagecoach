from __future__ import annotations

import os
from aiogram import Router, F
from aiogram.filters import StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.keyboards.reply import main_menu_kb, BTN_APPLY
from app.storage.repo_extras import save_leader_intent, save_premium_request

router = Router(name="leader")

ADMIN_ALERT_CHAT_ID = int(os.getenv("ADMIN_ALERT_CHAT_ID", "0"))

class LeaderStates(StatesGroup):
    intent = State()
    micro = State()     # ждём слово-ощущение
    premium = State()

INTENT_INSTR = {
    "voice": (
        "ГОЛОС · 2–4 мин\n"
        "• 30c — дыхание «вниз», 2 цикла.\n"
        "• 60–90c — «м-н-з» + фраза дня с 2–3 смысловыми паузами.\n"
        "• 15c — отметь 1 ощущение и цель, что улучшить."
    ),
    "public": (
        "ПУБЛИЧНЫЕ · 2–4 мин\n"
        "• 30c — выгода слушателя одной фразой.\n"
        "• 60–90c — тезис → пример → вывод.\n"
        "• 15c — 1 слово-итог + где ставил паузы."
    ),
    "stage": (
        "СЦЕНА · 2–4 мин\n"
        "• 30c — стойка: стопы, колени мягкие, центр внизу.\n"
        "• 60–90c — «маршрут» (3 точки) + текст, паузы в точках.\n"
        "• 15c — 1 слово-итог про тело/взгляд/энергию."
    ),
    "other": (
        "ДРУГОЕ · 2–4 мин\n"
        "• Возьми любую задачу и проговори тезис → мини-пример → вывод.\n"
        "• Сохрани 1 слово-ощущение в конце круга."
    ),
}

def _intent_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="Голос", callback_data="leader:intent:voice")
    kb.button(text="Публичные выступления", callback_data="leader:intent:public")
    kb.button(text="Сцена", callback_data="leader:intent:stage")
    kb.button(text="Другое", callback_data="leader:intent:other")
    kb.adjust(1)
    kb.button(text="🏠 В меню", callback_data="go:menu")
    return kb.as_markup()

def _ready_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="Готово", callback_data="leader:ready")
    kb.button(text="🏠 В меню", callback_data="go:menu")
    return kb.as_markup()

async def _entry_core(msg: Message, state: FSMContext):
    await state.set_state(LeaderStates.intent)
    await msg.answer(
        "Путь лидера — твой вектор. 3 шага, 2–4 минуты.\nЧто важнее сейчас?",
        reply_markup=_intent_kb(),
    )

@router.message(StateFilter("*"), F.text == BTN_APPLY)
@router.message(StateFilter("*"), Command("apply"))
async def start_leader(msg: Message, state: FSMContext):
    await _entry_core(msg, state)

@router.callback_query(StateFilter(LeaderStates.intent), F.data.startswith("leader:intent:"))
async def on_intent(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    intent = cb.data.split(":")[-1]
    await state.update_data(intent=intent)
    # первичная фиксация выбора
    try:
        await save_leader_intent(cb.from_user.id, intent=intent, micro_note=None)
    except Exception:
        pass

    await cb.message.answer(INTENT_INSTR.get(intent, INTENT_INSTR["other"]), reply_markup=_ready_kb())

@router.callback_query(StateFilter("*"), F.data == "leader:ready")
async def leader_ready(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.set_state(LeaderStates.micro)
    await cb.message.answer("Сделай круг. Одним словом: что изменилось? (до 140 симв)")

@router.message(StateFilter(LeaderStates.micro), F.text)
async def on_micro(msg: Message, state: FSMContext):
    note = (msg.text or "")[:140]
    data = await state.get_data()
    intent = data.get("intent", "other")
    try:
        await save_leader_intent(msg.from_user.id, intent=intent, micro_note=note, upsert=True)
    except Exception:
        pass

    await state.set_state(LeaderStates.premium)
    kb = InlineKeyboardBuilder()
    kb.button(text="Оставить заявку", callback_data="premium:leave")
    kb.button(text="Пропустить", callback_data="premium:skip")
    kb.button(text="🏠 В меню", callback_data="go:menu")
    kb.adjust(2, 1)
    await msg.answer(
        "Хочешь в ⭐️Расширенную? Напиши 1 фразу о цели (до 280 симв) или нажми «Пропустить».",
        reply_markup=kb.as_markup()
    )

@router.callback_query(StateFilter(LeaderStates.premium), F.data == "premium:skip")
async def premium_skip(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.clear()
    await cb.message.answer("Ок, без заявки. Возвращаю в меню.", reply_markup=main_menu_kb())

@router.callback_query(StateFilter(LeaderStates.premium), F.data == "premium:leave")
async def premium_leave(cb: CallbackQuery):
    await cb.answer()
    await cb.message.answer("Напиши 1 фразу о себе/задаче (до 280 симв).")

@router.message(StateFilter(LeaderStates.premium), F.text)
async def premium_text(msg: Message, state: FSMContext):
    text = (msg.text or "")[:280]
    data = await state.get_data()
    try:
        await save_premium_request(user_id=msg.from_user.id, text=text, source="leader")
    except Exception:
        pass

    # алерт админу (если задан)
    if ADMIN_ALERT_CHAT_ID:
        u = msg.from_user
        alert = (f"⭐️ Premium request\n"
                 f"User: {u.full_name} (@{u.username}) id {u.id}\n"
                 f"Intent: {data.get('intent','n/a')}\n"
                 f"Source: leader\n"
                 f"Text: {text}")
        try:
            await msg.bot.send_message(ADMIN_ALERT_CHAT_ID, alert)
        except Exception:
            pass

    await state.clear()
    await msg.answer("✅ Заявка принята. Мы вернёмся с предложением.", reply_markup=main_menu_kb())
