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
from app.storage.repo_extras import save_leader_intent  # upsert=True для заметки

router = Router(name="leader")

ADMIN_ALERT_CHAT_ID = int(os.getenv("ADMIN_ALERT_CHAT_ID", "0") or 0)

class LeaderStates(StatesGroup):
    intent = State()
    micro = State()

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
    await state.set_state(LeaderStates.intent)
    await msg.answer(
        "Путь лидера — твой вектор. 3 шага, 2–4 минуты.\nЧто важнее сейчас?",
        reply_markup=intent_kb(),
    )

# старт из кнопки нижнего меню
@router.message(StateFilter("*"), F.text == BTN_APPLY)
async def start_leader_btn(msg: Message, state: FSMContext):
    await _start_leader_core(msg, state)

# старт по /apply
@router.message(StateFilter("*"), Command("apply"))
async def start_leader_cmd(msg: Message, state: FSMContext):
    await _start_leader_core(msg, state)

# старт из inline (help/go:apply)
@router.callback_query(StateFilter("*"), F.data == "go:apply")
async def start_leader_cb(cb: CallbackQuery, state: FSMContext):
    await _start_leader_core(cb.message, state)
    await cb.answer()

@router.callback_query(StateFilter(LeaderStates.intent), F.data.startswith("leader:intent:"))
async def on_intent(cb: CallbackQuery, state: FSMContext):
    intent = cb.data.split(":")[-1]
    await state.update_data(intent=intent)
    # первичная запись (без заметки)
    await save_leader_intent(cb.from_user.id, intent=intent, micro_note=None, upsert=False)
    await state.set_state(LeaderStates.micro)
    await cb.message.answer("Сделай 1 круг. Одним словом: что изменилось? (до 140 симв)", reply_markup=menu_btn())
    await cb.answer()

@router.message(StateFilter(LeaderStates.micro))
async def on_micro(msg: Message, state: FSMContext):
    data = await state.get_data()
    note = (msg.text or "").strip()[:140]
    await save_leader_intent(msg.from_user.id, intent=data["intent"], micro_note=note, upsert=True)
    # финальный отклик
    await msg.answer("✅ Заявка принята. Мы вернёмся с предложением.", reply_markup=main_menu_kb())
    await state.clear()
