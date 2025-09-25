# app/routers/leader.py
from __future__ import annotations

import os
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from app.keyboards.reply import main_menu_kb, BTN_APPLY
from app.keyboards.inline import leader_intent_kb, leader_skip_kb
from app.storage.repo_extras import save_leader_intent, save_premium_request  # оставим как есть

router = Router(name="leader")

ADMIN_ALERT_CHAT_ID = int(os.getenv("ADMIN_ALERT_CHAT_ID", "0") or 0)

class Leader(StatesGroup):
    waiting_micro = State()    # короткая заметка «одним словом»
    waiting_request = State()  # опциональная фраза для premium-заявки

async def _start(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer(
        "Путь лидера — твой вектор. 3 шага, 2–4 минуты.\nЧто важнее сейчас?",
        reply_markup=leader_intent_kb(),
    )

# старт и по кнопке, и по команде
@router.message(StateFilter("*"), F.text == BTN_APPLY)
async def start_leader_btn(msg: Message, state: FSMContext):
    await _start(msg, state)

@router.message(StateFilter("*"), Command("apply"))
async def start_leader_cmd(msg: Message, state: FSMContext):
    await _start(msg, state)

# ЕДИНЫЙ разбор leader:* (intent/menu/skip/submit ...)
@router.callback_query(StateFilter("*"), F.data.startswith("leader:"))
async def leader_router(cb: CallbackQuery, state: FSMContext):
    # leader:<action>:<value?>
    parts = (cb.data or "").split(":")
    action = parts[1] if len(parts) > 1 else ""
    value  = parts[2] if len(parts) > 2 else None

    if action == "intent":
        intent = value or "other"
        await state.update_data(intent=intent)
        # первичная запись (без заметки)
        try:
            await save_leader_intent(cb.from_user.id, intent=intent, micro_note=None)
        except Exception:
            pass
        await cb.message.edit_reply_markup()  # снимаем старые кнопки
        await cb.message.answer("Сделай 1 круг. Одним словом: что изменилось? (до 140 симв)", reply_markup=leader_skip_kb())
        await state.set_state(Leader.waiting_micro)
        return await cb.answer()

    if action in {"menu", "skip"}:
        await state.clear()
        await cb.message.edit_reply_markup()
        await cb.message.answer("Готово! Открываю меню.", reply_markup=main_menu_kb())
        return await cb.answer()

    # неизвестное действие — не молчим
    await cb.answer("Команда обновлена. Нажми «В меню» и попробуй снова.", show_alert=False)

@router.message(StateFilter(Leader.waiting_micro), F.text)
async def leader_micro_note(msg: Message, state: FSMContext):
    note = (msg.text or "").strip()[:140]
    data = await state.get_data()
    intent = data.get("intent", "other")
    try:
        await save_leader_intent(msg.from_user.id, intent=intent, micro_note=note, upsert=True)
    except Exception:
        pass

    # Предложим оставить короткую цель (premium request) ИЛИ сразу в меню.
    await msg.answer("Оставь 1 фразу о цели (до 280 симв) — поможем подобрать формат.\nИли нажми «В меню».", reply_markup=leader_skip_kb())
    await state.set_state(Leader.waiting_request)

@router.message(StateFilter(Leader.waiting_request), F.text)
async def leader_premium_request(msg: Message, state: FSMContext):
    text = (msg.text or "").strip()[:280]
    try:
        await save_premium_request(user_id=msg.from_user.id, text=text, source="leader")
        if ADMIN_ALERT_CHAT_ID:
            u = msg.from_user
            await msg.bot.send_message(
                ADMIN_ALERT_CHAT_ID,
                f"⭐️ Premium request\n"
                f"User: {u.full_name} (@{u.username}) id {u.id}\n"
                f"Text: {text}"
            )
    except Exception:
        pass

    await state.clear()
    await msg.answer("✅ Заявка принята. Мы вернёмся с предложением.", reply_markup=main_menu_kb())
