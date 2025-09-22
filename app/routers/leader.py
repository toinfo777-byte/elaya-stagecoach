# app/routers/leader.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.storage.repo_extras import save_leader_intent, save_premium_request
from app.keyboards.reply import main_menu_kb, BTN_APPLY
import os

router = Router(name="leader")

ADMIN_ALERT_CHAT_ID = int(os.getenv("ADMIN_ALERT_CHAT_ID", "0"))

class LeaderFSM(StatesGroup):
    intent = State()
    micro = State()
    premium = State()

def intent_kb():
    kb = InlineKeyboardBuilder()
    for tag, text in [("voice","Голос"),("public","Публичные выступления"),("stage","Сцена"),("other","Другое")]:
        kb.button(text=text, callback_data=f"intent:{tag}")
    kb.button(text="В меню", callback_data="leader:menu")
    kb.adjust(2,2,1)
    return kb.as_markup()

@router.message(F.text == BTN_APPLY)
async def leader_start(msg: Message, state: FSMContext):
    await state.set_state(LeaderFSM.intent)
    await msg.answer("Путь лидера — твой вектор. 3 шага, 2–4 минуты.\nЧто важнее сейчас?", reply_markup=intent_kb())

@router.callback_query(F.data.startswith("intent:"), LeaderFSM.intent)
async def select_intent(cb: CallbackQuery, state: FSMContext):
    intent = cb.data.split(":",1)[1]
    await state.update_data(intent=intent)
    await save_leader_intent(cb.from_user.id, intent=intent, micro_note=None)
    await state.set_state(LeaderFSM.micro)
    await cb.message.edit_text("Сделай 1 круг. Одним словом: что изменилось? (до 140 симв)")
    await cb.answer()

@router.callback_query(F.data=="leader:menu")
async def leader_menu(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.message.answer("В меню.", reply_markup=main_menu_kb())
    await cb.answer()

@router.message(LeaderFSM.micro, F.text)
async def micro_note(msg: Message, state: FSMContext):
    note = (msg.text or "")[:140]
    data = await state.get_data()
    await save_leader_intent(msg.from_user.id, intent=data["intent"], micro_note=note, upsert=True)
    await state.set_state(LeaderFSM.premium)
    kb = InlineKeyboardBuilder()
    kb.button(text="Оставить заявку", callback_data="premium:leave")
    kb.button(text="Пропустить", callback_data="premium:skip")
    kb.button(text="В меню", callback_data="leader:menu")
    kb.adjust(2,1)
    await msg.answer("Хочешь в расширенную? Оставь 1 фразу о цели. Это поможет подобрать формат.", reply_markup=kb.as_markup())

@router.callback_query(F.data=="premium:skip", LeaderFSM.premium)
async def premium_skip(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.message.answer("Ок, без заявки. Возвращаю в меню.", reply_markup=main_menu_kb())
    await cb.answer()

@router.callback_query(F.data=="premium:leave", LeaderFSM.premium)
async def premium_leave(cb: CallbackQuery):
    await cb.message.edit_text("Напиши 1 фразу о себе/задаче (до 280 симв).")
    await cb.answer()

@router.message(LeaderFSM.premium, F.text)
async def premium_text(msg: Message, state: FSMContext):
    text = (msg.text or "")[:280]
    data = await state.get_data()
    await save_premium_request(msg.from_user.id, text=text, source="leader")
    if ADMIN_ALERT_CHAT_ID:
        u = msg.from_user
        intent = data.get("intent", "n/a")
        alert = (f"⭐️ Premium request\n"
                 f"User: {u.full_name} (@{u.username}) id {u.id}\n"
                 f"Intent: {intent}\n"
                 f"Source: leader\n"
                 f"Text: {text}")
        try:
            await msg.bot.send_message(ADMIN_ALERT_CHAT_ID, alert)
        except Exception:
            pass
    await state.clear()
    await msg.answer("Заявка принята. Мы свяжемся с тобой.", reply_markup=main_menu_kb())
