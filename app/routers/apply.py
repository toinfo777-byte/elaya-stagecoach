# app/routers/apply.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from app.storage.repo import session_scope, log_event
from app.storage.models import Lead, User

router = Router(name="apply")

# --- Клавиатуры --------------------------------------------------------------

KB_APPLY_DONE = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📅 Хочу созвон"), KeyboardButton(text="✍️ Изменить заявку")],
        [KeyboardButton(text="🏠 В меню")],
    ],
    resize_keyboard=True,
)

KB_APPLY_START = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🏠 В меню")]],
    resize_keyboard=True,
)

# --- Состояния (если у вас нет своей FSM) -----------------------------------

from aiogram.fsm.state import State, StatesGroup

class ApplyStates(StatesGroup):
    typing = State()


# --- Handlers ----------------------------------------------------------------

@router.message(F.text == "🧭 Путь лидера")
@router.message(F.text == "/apply")
async def on_apply_start(m: Message, state: FSMContext, user: User):
    await state.set_state(ApplyStates.typing)
    await m.answer(
        "Путь лидера: короткая заявка.\nНапишите, чего хотите достичь — одним сообщением.",
        reply_markup=KB_APPLY_START,
    )


@router.message(ApplyStates.typing, F.text.len() > 1)
async def on_apply_text(m: Message, state: FSMContext, user: User):
    text = m.text.strip()

    with session_scope() as s:
        s.add(
            Lead(
                user_id=user.id,
                channel="tg",
                contact=f"@{user.username or '-'}",
                note=text,
                track="apply",
            )
        )
        s.commit()
        log_event(s, user.id, "apply_submitted", {"len": len(text)})

    await state.clear()
    await m.answer("Спасибо! Принял. Двигаемся дальше 👍", reply_markup=KB_APPLY_DONE)


@router.message(F.text == "📅 Хочу созвон")
async def on_apply_call(m: Message, user: User):
    # Здесь поставьте вашу инструкцию/ссылку/контакт
    await m.answer(
        "Отлично! Напишите @your_manager, или пришлите номер — подберём время созвона.\n"
        "Можно просто отправить телефон одним сообщением."
    )


@router.message(F.text == "✍️ Изменить заявку")
async def on_apply_edit(m: Message, state: FSMContext, user: User):
    await state.set_state(ApplyStates.typing)
    await m.answer("Ок! Пришлите новую формулировку заявки одним сообщением.")


@router.message(F.text == "🏠 В меню")
async def on_back_to_menu(m: Message, user: User):
    from app.keyboards.menu import main_menu
    await m.answer("Вернулись в меню.", reply_markup=main_menu())
