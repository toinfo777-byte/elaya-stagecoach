# app/routers/leader.py
from __future__ import annotations

import os
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.keyboards.reply import main_menu_kb, BTN_APPLY
from app.keyboards.common import menu_btn
from app.storage.repo_extras import save_leader_intent, save_premium_request

router = Router(name="leader")

ADMIN_ALERT_CHAT_ID = int(os.getenv("ADMIN_ALERT_CHAT_ID", "0") or 0)

class LeaderStates(StatesGroup):
    micro = State()
    premium = State()

def intent_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="Голос", callback_data="leader:intent:voice")
    kb.button(text="Публичные выступления", callback_data="leader:intent:public")
    kb.button(text="Сцена", callback_data="leader:intent:stage")
    kb.button(text="Другое", callback_data="leader:intent:other")
    kb.button(text="🏠 В меню", callback_data="go:menu")
    kb.adjust(1)
    return kb.as_markup()

async def _start_leader_core(msg: Message, state: FSMContext):
    await state.clear()
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

@router.callback_query(F.data == "go:apply")
async def start_leader_from_help(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await _start_leader_core(cb.message, state)

@router.callback_query(F.data.startswith("leader:intent:"))
async def on_intent(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    intent = cb.data.split(":")[-1]
    await state.update_data(intent=intent)
    # первичная запись (без заметки)
    try:
        await save_leader_intent(cb.from_user.id, intent=intent, micro_note=None)
    except Exception:
        pass
    await cb.message.answer(
        "Сделай 1 круг. Одним словом: что изменилось? (до 140 симв)",
        reply_markup=menu_btn()
    )
    await state.set_state(LeaderStates.micro)

@router.message(StateFilter(LeaderStates.micro), F.text)
async def on_micro(msg: Message, state: FSMContext):
    note = (msg.text or "").strip()[:140]
    data = await state.get_data()
    try:
        await save_leader_intent(msg.from_user.id, intent=data.get("intent","other"), micro_note=note, upsert=True)
    except Exception:
        pass
    await msg.answer(
        "Оставь 1 фразу о цели для ⭐ Расширенной версии (до 280 симв) или нажми «🏠 В меню».",
        reply_markup=menu_btn()
    )
    await state.set_state(LeaderStates.premium)

@router.message(StateFilter(LeaderStates.premium), F.text)
async def on_premium_text(msg: Message, state: FSMContext):
    data = await state.get_data()
    text = (msg.text or "")[:280]
    try:
        await save_premium_request(user_id=msg.from_user.id, text=text, source="leader")
    except Exception:
        pass
    if ADMIN_ALERT_CHAT_ID:
        u = msg.from_user
        alert = (f"⭐️ Premium request\n"
                 f"User: {u.full_name} (@{u.username}) id {u.id}\n"
                 f"Intent: {data.get('intent')}\n"
                 f"Source: leader\n"
                 f"Text: {text}")
        try:
            await msg.bot.send_message(ADMIN_ALERT_CHAT_ID, alert)
        except Exception:
            pass
    await state.clear()
    await msg.answer("✅ Заявка принята. Мы вернёмся с предложением.", reply_markup=main_menu_kb())
