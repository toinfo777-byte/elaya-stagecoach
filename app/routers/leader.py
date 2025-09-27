# app/routers/leader.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

router = Router(name="leader")

class LeaderState(StatesGroup):
    wait_note = State()

def _kb_topics() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Голос",                   callback_data="leader:topic:voice")],
        [InlineKeyboardButton(text="Публичные выступления",   callback_data="leader:topic:public")],
        [InlineKeyboardButton(text="Сцена",                   callback_data="leader:topic:stage")],
        [InlineKeyboardButton(text="🏠 В меню",               callback_data="go:menu")],
    ])

async def leader_entry(obj: Message | CallbackQuery):
    text = "Путь лидера — твой вектор. 3 шага, 2–4 минуты.\nЧто важнее сейчас?"
    if isinstance(obj, CallbackQuery):
        await obj.answer()
        await obj.message.answer(text, reply_markup=_kb_topics())
    else:
        await obj.answer(text, reply_markup=_kb_topics())

@router.message(Command("apply"))
async def cmd_apply(m: Message):
    await leader_entry(m)

@router.callback_query(StateFilter("*"), F.data.startswith("leader:topic:"))
async def pick_topic(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    intent = cb.data.split(":")[-1]
    await state.update_data(intent=intent)
    await state.set_state(LeaderState.wait_note)
    await cb.message.answer(
        "Сделай 1 круг (2–3 мин) по теме. Одним словом: что изменилось? (до 140 симв)\n"
        "Когда будешь готов — просто напиши."
    )

@router.message(LeaderState.wait_note, F.text.len() > 0)
async def save_note(m: Message, state: FSMContext):
    try:
        from app.storage.repo_extras import log_progress_event
        await log_progress_event(m.from_user.id, kind="leader_path", meta=None)
    except Exception:
        pass
    await state.clear()
    from app.routers.help import show_main_menu
    await m.answer("✅ Принято. Возвращаю в меню.")
    await show_main_menu(m)
