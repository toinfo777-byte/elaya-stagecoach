from __future__ import annotations

from datetime import datetime
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters.state import StateFilter
from aiogram.types import Message

from app.texts.strings import (
    HELLO,
    CONSENT,
    ONBOARD_GOAL_PROMPT,
    ONBOARD_EXP_PROMPT,
    ONBOARD_TZ_PROMPT,
    ONBOARD_NAME_PROMPT,
)
from app.keyboards.menu import main_menu
from app.storage.repo import session_scope
from app.storage.models import User

router = Router(name="onboarding")


class Onboarding(StatesGroup):
    name = State()
    tz = State()
    goal = State()
    exp = State()
    consent = State()


def extract_start_payload(text: str | None) -> str | None:
    """
    Забираем payload из /start <payload>.
    До 64 символов (лимит Telegram). Никакой декодировки не делаем, чтобы не ломать короткие коды.
    Рекомендуем форматить коды как: src_vk_sep, src_tg_chX, ad_gdn_01 и т.п.
    """
    if not text:
        return None
    parts = text.split(maxsplit=1)
    if len(parts) == 2 and parts[0].startswith("/start"):
        return parts[1].strip()[:64]
    return None


def _bump_sources_meta(u: User, src: str | None) -> None:
    """
    Храним «первый» и «последний» источник в meta_json, а также плоское поле user.source.
    - user.source заполняем только если ещё пусто (источник привлечения)
    - meta.sources.first_source / last_source обновляем всегда по факту текущего входа
    """
    if not src:
        return
    # плоское поле для простых отчётов
    if not getattr(u, "source", None):
        u.source = src[:64]

    # аккуратно обновим meta_json
    meta = {}
    try:
        meta = dict(u.meta_json or {}) if hasattr(u, "meta_json") and u.meta_json else {}
    except Exception:
        meta = {}

    sources = dict(meta.get("sources") or {})
    if not sources.get("first_source"):
        sources["first_source"] = src[:64]
    sources["last_source"] = src[:64]
    meta["sources"] = sources
    try:
        u.meta_json = meta  # type: ignore[attr-defined]
    except Exception:
        # если в модели нет meta_json — просто молча пропустим
        pass


@router.message(StateFilter(None), CommandStart())
async def start(msg: Message, state: FSMContext):
    payload = extract_start_payload(msg.text)
    if payload:
        await state.update_data(source=payload)
    await msg.answer(HELLO)
    await msg.answer(ONBOARD_NAME_PROMPT)
    await state.set_state(Onboarding.name)


@router.message(~StateFilter(None), Command("cancel"))
async def cancel_anywhere(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer("Анкета сброшена. Возвращаю в меню.", reply_markup=main_menu())

@router.message(~StateFilter(None), Command("menu"))
async def menu_anywhere(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer("Готово. Вот меню:", reply_markup=main_menu())

@router.message(~StateFilter(None), CommandStart())
async def restart_anywhere(msg: Message, state: FSMContext):
    await state.clear()
    await start(msg, state)


@router.message(~StateFilter(None), F.text.startswith("/"))
async def in_form_but_command(msg: Message):
    await msg.answer("Вы сейчас заполняете короткую анкету. Напишите ответ или /cancel, чтобы выйти.")


@router.message(Onboarding.name, ~F.text.startswith("/"))
async def set_name(msg: Message, state: FSMContext):
    await state.update_data(name=(msg.text or "").strip())
    await msg.answer(ONBOARD_TZ_PROMPT)
    await state.set_state(Onboarding.tz)

@router.message(Onboarding.tz, ~F.text.startswith("/"))
async def set_tz(msg: Message, state: FSMContext):
    await state.update_data(tz=(msg.text or "").strip())
    await msg.answer(ONBOARD_GOAL_PROMPT)
    await state.set_state(Onboarding.goal)

@router.message(Onboarding.goal, ~F.text.startswith("/"))
async def set_goal(msg: Message, state: FSMContext):
    await state.update_data(goal=(msg.text or "").strip())
    await msg.answer(ONBOARD_EXP_PROMPT)
    await state.set_state(Onboarding.exp)

@router.message(Onboarding.exp, ~F.text.startswith("/"))
async def set_exp(msg: Message, state: FSMContext):
    try:
        exp = int((msg.text or "").strip())
    except Exception:
        exp = 0
    await state.update_data(exp=exp)
    await msg.answer(CONSENT + "\n\nНапишите «Согласен».")
    await state.set_state(Onboarding.consent)

@router.message(Onboarding.consent, ~F.text.startswith("/"))
async def finalize(msg: Message, state: FSMContext):
    data = await state.get_data()
    with session_scope() as s:
        u = s.query(User).filter_by(tg_id=msg.from_user.id).first()
        if not u:
            u = User(tg_id=msg.from_user.id)
        u.username = msg.from_user.username
        u.name = data.get("name")
        u.tz = data.get("tz")
        u.goal = data.get("goal")
        u.exp_level = int(data.get("exp") or 0)
        u.consent_at = datetime.utcnow()

        src = (data.get("source") or "").strip() or None
        if src:
            _bump_sources_meta(u, src)

        s.add(u)
    await state.clear()
    await msg.answer("Готово. Добро пожаловать в меню.", reply_markup=main_menu())
