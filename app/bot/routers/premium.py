# app/bot/routers/premium.py
from __future__ import annotations

from aiogram import Router, F, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from app.keyboards.menu import (
    main_menu,
    BTN_PREMIUM,       # ⭐️ Расширенная версия
)
from app.storage.models import User, Lead
from app.storage.repo import session_scope

router = Router(name="premium")


# ----- FSM -----
class PremiumForm(StatesGroup):
    waiting_text = State()   # ждём короткую заявку


# ----- Вспомогательное -----
def _contact_from_tg(user: types.User) -> str:
    if user.username:
        return f"@{user.username}"
    return f"tg:{user.id}"


def _get_or_create_user(tg_user: types.User) -> User:
    with session_scope() as s:
        u: User | None = s.query(User).filter_by(tg_id=tg_user.id).first()
        if u is None:
            u = User(
                tg_id=tg_user.id,
                username=tg_user.username,
                name=tg_user.full_name,
            )
            s.add(u)
            s.commit()
            s.refresh(u)
        return u


# ----- Клавиатуры локальные -----
def premium_menu_kb() -> types.ReplyKeyboardMarkup:
    rows = [
        [types.KeyboardButton(text="Что внутри")],
        [types.KeyboardButton(text="Оставить заявку")],
        [types.KeyboardButton(text="Мои заявки")],
        [types.KeyboardButton(text="📯 В меню")],
    ]
    return types.ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


# ----- Хендлеры: вход в раздел -----
@router.message(Command("premium"))
@router.message(F.text == BTN_PREMIUM)
async def premium_entry(message: types.Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "⭐️ <b>Расширенная версия</b>\n\n"
        "• Ежедневный разбор и обратная связь\n"
        "• Разогрев голоса, дикции и внимания\n"
        "• Мини-кастинг и путь лидера\n\n"
        "Выберите действие:",
        reply_markup=premium_menu_kb(),
    )


# ----- Что внутри -----
@router.message(F.text == "Что внутри")
async def premium_inside(message: types.Message) -> None:
    await message.answer(
        "Внутри:\n"
        "• Живые мини-разборы с обратной связью\n"
        "• Пакеты «голос/дикция/внимание» на каждый день\n"
        "• Кастинг-вопросы и «путь лидера» для заявки",
        reply_markup=premium_menu_kb(),
    )


# ----- Оставить заявку -----
@router.message(F.text == "Оставить заявку")
async def premium_apply_start(message: types.Message, state: FSMContext) -> None:
    await state.set_state(PremiumForm.waiting_text)
    await message.answer(
        "Оставьте короткую заявку (до 200 символов):\n"
        "какая цель, что хотите получить? Если передумали — /cancel",
    )


@router.message(Command("cancel"), StateFilter(PremiumForm.waiting_text))
async def premium_apply_cancel(message: types.Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Ок, вернулись в главное меню. Нажми нужную кнопку снизу.", reply_markup=main_menu())


@router.message(StateFilter(PremiumForm.waiting_text))
async def premium_apply_save(message: types.Message, state: FSMContext) -> None:
    text = (message.text or "").strip()
    if not text:
        await message.answer("Пришлите, пожалуйста, заявку одним сообщением.")
        return

    u = _get_or_create_user(message.from_user)
    with session_scope() as s:
        s.add(Lead(
            user_id=u.id,
            channel="tg",
            contact=_contact_from_tg(message.from_user),
            note=text[:500],
            track="premium",     # отличаем от leader
        ))
        s.commit()

    await state.clear()
    await message.answer("Спасибо! Принял ✅ (без записи в БД). Мы свяжемся или включим доступ автоматически.", reply_markup=premium_menu_kb())


# ----- Мои заявки -----
@router.message(F.text == "Мои заявки")
async def premium_my_requests(message: types.Message) -> None:
    u = _get_or_create_user(message.from_user)
    with session_scope() as s:
        rows: list[Lead] = (
            s.query(Lead)
            .filter(Lead.user_id == u.id)
            .order_by(Lead.ts.desc())
            .limit(5)
            .all()
        )

    if not rows:
        await message.answer("Заявок пока нет.", reply_markup=premium_menu_kb())
        return

    # Красивый список (с треком)
    lines = []
    for i, r in enumerate(rows, start=1):
        lines.append(f"• #{i} — {r.ts:%d.%m %H:%M} — {r.track or '—'}")

    await message.answer("Мои заявки:\n" + "\n".join(lines), reply_markup=premium_menu_kb())


# ----- Выход в главное меню -----
@router.message(F.text == "📯 В меню")
async def back_to_main(message: types.Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Ок, вернулись в главное меню. Нажми нужную кнопку снизу.", reply_markup=main_menu())
