from __future__ import annotations
from aiogram import Router, F
from aiogram.filters import Command
from aiagram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from app.keyboards.menu import main_menu
from app.storage.repo import session_scope
from app.storage.models import User
from app.services.leads import create_lead, LeadPayload

router = Router(name="premium")


OFFERS_TEXT = (
    "⭐ *Расширенная версия*\n\n"
    "• Персональный трек — 4 недели\n"
    "• Мини-группа «Проба сцены»\n\n"
    "Оставьте контакт — свяжемся и подскажем, что подойдёт лучше."
)

def _offers_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Оставить контакт", callback_data="lead_start")],
        [InlineKeyboardButton(text="Назад в меню", callback_data="lead_back")],
    ])

class LeadFSM(StatesGroup):
    channel = State()
    contact = State()
    note = State()

def _channels_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Telegram", callback_data="ch_telegram"),
            InlineKeyboardButton(text="WhatsApp", callback_data="ch_whatsapp"),
        ],
        [
            InlineKeyboardButton(text="Email", callback_data="ch_email"),
            InlineKeyboardButton(text="ch другой", callback_data="ch_other"),
        ],
    ])

@router.message(F.text == "⭐ Расширенная версия")
@router.message(Command("premium"))
async def show_offers(m: Message):
    await m.answer(OFFERS_TEXT, reply_markup=_offers_kb(), parse_mode="Markdown")

@router.callback_query(F.data == "lead_back")
async def lead_back(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.message.answer("Меню:", reply_markup=main_menu())
    await cb.answer()

@router.callback_query(F.data == "lead_start")
async def lead_start(cb: CallbackQuery, state: FSMContext):
    await state.set_state(LeadFSM.channel)
    await cb.message.edit_text(
        "Выберите предпочитаемый канал связи:", reply_markup=_channels_kb()
    )
    await cb.answer()

@router.callback_query(LeadFSM.channel, F.data.startswith("ch_"))
async def lead_choose_channel(cb: CallbackQuery, state: FSMContext):
    ch = cb.data.removeprefix("ch_")
    await state.update_data(channel=ch)
    # Предзаполнение телеграма, если есть username
    prefill = ""
    if ch == "telegram" and cb.from_user.username:
        prefill = f"@{cb.from_user.username}"
    await state.set_state(LeadFSM.contact)
    await cb.message.edit_text(
        "Оставьте контакт (ник/телефон/email). Пример: `@elaya_school` или `+79001234567`",
        parse_mode="Markdown",
    )
    if prefill:
        await cb.message.answer(f"Подходит этот контакт?\n{prefill}\nЕсли да — просто отправьте его.")
    await cb.answer()

@router.message(LeadFSM.contact, F.text.len() > 0)
async def lead_save_contact(m: Message, state: FSMContext):
    await state.update_data(contact=m.text.strip())
    await state.set_state(LeadFSM.note)
    await m.answer("Коротко: чем помочь? (опционально). Или пришлите «-»")
    
@router.message(LeadFSM.note, F.text.len() > 0)
async def lead_save_note(m: Message, state: FSMContext):
    d = await state.get_data()
    note = m.text if m.text != "-" else ""
    with session_scope() as s:
        u = s.query(User).filter_by(tg_id=m.from_user.id).first()
        if not u:
            await m.answer("Сначала /start для онбординга.", reply_markup=main_menu())
            await state.clear()
            return
        create_lead(
            s, u.id,
            LeadPayload(channel=d["channel"], contact=d["contact"], note=note)
        )
    await state.clear()
    await m.answer("Спасибо! Контакт записан. Мы свяжемся. 🙌", reply_markup=main_menu())
