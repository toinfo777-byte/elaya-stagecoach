from __future__ import annotations

from aiogram import Router, F, types
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from app.ui.keyboards import main_menu, BTN_APPLY
from app.storage.repo import session_scope
from app.storage.models import User, Lead

router = Router(name="apply")

K_APPLY_SUBMIT = "Оставить заявку"
K_BACK = "📣 В меню"

def apply_kb() -> types.ReplyKeyboardMarkup:
    rows = [
        [types.KeyboardButton(text=K_APPLY_SUBMIT)],
        [types.KeyboardButton(text=K_BACK)],
    ]
    return types.ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True, is_persistent=True)

class ApplyForm(StatesGroup):
    waiting_goal = State()


@router.message(F.text == BTN_APPLY)
@router.message(F.text == "/apply")
async def apply_entry(m: types.Message, state: FSMContext):
    await state.clear()
    await m.answer(
        "🧭 <b>Путь лидера</b> — индивидуальная траектория с фокусом на цели.\n"
        "Оставьте заявку — вернусь с вопросами и предложениями.",
        reply_markup=apply_kb(),
    )


@router.message(F.text == K_APPLY_SUBMIT)
async def apply_submit(m: types.Message, state: FSMContext):
    await state.set_state(ApplyForm.waiting_goal)
    await m.answer(
        "Короткая заявка. Напишите, чего хотите достичь — одним сообщением (до 200 символов).\n"
        "Если передумали — /cancel.",
        reply_markup=apply_kb(),
    )


@router.message(ApplyForm.waiting_goal, F.text.len() > 0)
async def apply_save(m: types.Message, state: FSMContext):
    goal = (m.text or "").strip()[:200]
    tg_id = m.from_user.id

    with session_scope() as s:
        user = s.query(User).filter_by(tg_id=tg_id).first()
        if not user:
            user = User(tg_id=tg_id, username=m.from_user.username or None, name=m.from_user.full_name)
            s.add(user)
            s.flush()
        s.add(Lead(user_id=user.id, channel="tg", contact=f"@{m.from_user.username}" if m.from_user.username else "tg",
                   note=goal, track="apply"))

    await state.clear()
    await m.answer("Заявка принята ✅ (без записи в БД)", reply_markup=apply_kb())
    # ↑ если хотите писать в отдельную таблицу — поменяйте текст и оставьте как «с записью в БД» (мы уже пишем в Lead).


@router.message(F.text == K_BACK)
async def apply_back(m: types.Message, state: FSMContext):
    await state.clear()
    await m.answer("Ок, вернулись в главное меню. Нажми нужную кнопку снизу.", reply_markup=main_menu())
