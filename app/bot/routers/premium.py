from __future__ import annotations

from aiogram import Router, F, types
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from app.ui.keyboards import main_menu, BTN_PREMIUM  # твой модуль с кнопками
from app.storage.repo import session_scope
from app.storage.models import User, Lead

router = Router(name="premium")

# Локальные кнопки раздела
K_WHATS_INSIDE = "Что внутри"
K_APPLY = "Оставить заявку"
K_MY_REQUESTS = "Мои заявки"
K_BACK = "📣 В меню"

def premium_kb() -> types.ReplyKeyboardMarkup:
    rows = [
        [types.KeyboardButton(text=K_WHATS_INSIDE)],
        [types.KeyboardButton(text=K_APPLY)],
        [types.KeyboardButton(text=K_MY_REQUESTS), types.KeyboardButton(text=K_BACK)],
    ]
    return types.ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True, is_persistent=True)

class PremiumForm(StatesGroup):
    waiting_goal = State()


# ——— Вход в раздел
@router.message(F.text == BTN_PREMIUM)
@router.message(F.text == "/premium")
async def premium_entry(m: types.Message, state: FSMContext):
    await state.clear()
    text = (
        "⭐️ <b>Расширенная версия</b>\n\n"
        "• Ежедневный разбор и обратная связь\n"
        "• Разогрев голоса, дикции и внимания\n"
        "• Мини-кастинг и путь лидера\n\n"
        "<i>Выберите действие:</i>"
    )
    await m.answer(text, reply_markup=premium_kb())


# ——— Что внутри
@router.message(F.text == K_WHATS_INSIDE)
async def premium_inside(m: types.Message):
    await m.answer(
        "Внутри — тренировки, разбор речевых задач и сопровождение.\n"
        "Можно начать с короткой заявки — нажмите «Оставить заявку».",
        reply_markup=premium_kb(),
    )


# ——— Мои заявки
@router.message(F.text == K_MY_REQUESTS)
async def premium_my_requests(m: types.Message):
    tg_id = m.from_user.id
    with session_scope() as s:
        user = s.query(User).filter_by(tg_id=tg_id).first()
        items: list[Lead] = []
        if user:
            items = (
                s.query(Lead)
                .filter(Lead.user_id == user.id, Lead.track.in_(["premium", "apply"]))
                .order_by(Lead.id.desc())
                .limit(3)
                .all()
            )

    if not items:
        await m.answer("Заявок пока нет.", reply_markup=premium_kb())
        return

    lines = ["<b>Мои заявки:</b>"]
    for i, it in enumerate(items, 1):
        lines.append(f"• #{i} — {it.ts:%d.%m %H:%M} — {it.track} — «{it.note}»")
    await m.answer("\n".join(lines), reply_markup=premium_kb())


# ——— Оставить заявку → ввод цели
@router.message(F.text == K_APPLY)
async def premium_apply_start(m: types.Message, state: FSMContext):
    await state.set_state(PremiumForm.waiting_goal)
    await m.answer(
        "Напишите цель одной короткой фразой (до 200 символов).\n"
        "Если передумали — отправьте /cancel.",
        reply_markup=premium_kb(),
    )


@router.message(PremiumForm.waiting_goal, F.text.len() > 0)
async def premium_apply_save(m: types.Message, state: FSMContext):
    goal = (m.text or "").strip()[:200]
    tg_id = m.from_user.id

    with session_scope() as s:
        user = s.query(User).filter_by(tg_id=tg_id).first()
        if not user:
            user = User(tg_id=tg_id, username=m.from_user.username or None, name=m.from_user.full_name)
            s.add(user)
            s.flush()
        s.add(Lead(user_id=user.id, channel="tg", contact=f"@{m.from_user.username}" if m.from_user.username else "tg",
                   note=goal, track="premium"))

    await state.clear()
    await m.answer("Спасибо! Принял. Двигаемся дальше 👍", reply_markup=premium_kb())


# ——— Выход в главное меню
@router.message(F.text == K_BACK)
async def premium_back_to_menu(m: types.Message, state: FSMContext):
    await state.clear()
    await m.answer("Ок, вернулись в главное меню. Нажми нужную кнопку снизу.", reply_markup=main_menu())
