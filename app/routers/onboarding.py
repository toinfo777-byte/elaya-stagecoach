# app/routers/onboarding.py

from datetime import datetime
from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart
from app.keyboards.menu import main_menu
from app.storage.repo import session_scope
from app.storage.models import User

# ⬇️ безопасно подтягиваем тексты с дефолтами
try:
    from app.texts import strings as S  # ожидаемый модуль с константами
except Exception:
    class S:  # запасной план, если файла/констант нет
        HELLO = "Привет! Я — «Элайя — тренер сцены»."
        ONBOARD_NAME_PROMPT = "Как к тебе обращаться? Напиши имя, пожалуйста."
        ONBOARD_TZ_PROMPT = "В какой ты временной зоне? (например, Europe/Moscow или GMT+3)"
        ONBOARD_GOAL_PROMPT = "Какая у тебя цель на ближайший месяц на сцене?"
        ONBOARD_EXP_PROMPT = "Оцени свой опыт на сцене: 0..5 (целое число)"
        CONSENT = "Мы храним только минимум данных для работы. Согласен?"

def _t(name: str, default: str) -> str:
    return getattr(S, name, default)

HELLO              = _t("HELLO", "Привет! Я — «Элайя — тренер сцены».")
ONBOARD_NAME_PROMPT= _t("ONBOARD_NAME_PROMPT", "Как к тебе обращаться? Напиши имя.")
ONBOARD_TZ_PROMPT  = _t("ONBOARD_TZ_PROMPT", "Временная зона? (например, Europe/Moscow)")
ONBOARD_GOAL_PROMPT= _t("ONBOARD_GOAL_PROMPT", "Какая у тебя цель на ближайший месяц?")
ONBOARD_EXP_PROMPT = _t("ONBOARD_EXP_PROMPT", "Оцени свой опыт: 0..5")
CONSENT            = _t("CONSENT", "Мы храним только минимум данных. Согласен?")

class Onboarding(StatesGroup):
    name = State()
    tz   = State()
    goal = State()
    exp  = State()
    consent = State()

router = Router(name="onboarding")

@router.message(CommandStart())
async def start(msg: Message, state: FSMContext):
    await msg.answer(HELLO)
    await msg.answer(ONBOARD_NAME_PROMPT)
    await state.set_state(Onboarding.name)

@router.message(Onboarding.name)
async def set_name(msg: Message, state: FSMContext):
    await state.update_data(name=msg.text.strip())
    await msg.answer(ONBOARD_TZ_PROMPT)
    await state.set_state(Onboarding.tz)

@router.message(Onboarding.tz)
async def set_tz(msg: Message, state: FSMContext):
    await state.update_data(tz=msg.text.strip())
    await msg.answer(ONBOARD_GOAL_PROMPT)
    await state.set_state(Onboarding.goal)

@router.message(Onboarding.goal)
async def set_goal(msg: Message, state: FSMContext):
    await state.update_data(goal=msg.text.strip())
    await msg.answer(ONBOARD_EXP_PROMPT)
    await state.set_state(Onboarding.exp)

@router.message(Onboarding.exp)
async def set_exp(msg: Message, state: FSMContext):
    try:
        exp = int(msg.text.strip())
    except Exception:
        exp = 0
    await state.update_data(exp=exp)
    await msg.answer(CONSENT + "\n\nНапишите «Согласен».")
    await state.set_state(Onboarding.consent)

@router.message(Onboarding.consent)
async def finalize(msg: Message, state: FSMContext):
    data = await state.get_data()
    with session_scope() as s:
        user = s.query(User).filter_by(tg_id=msg.from_user.id).first() or User(tg_id=msg.from_user.id)
        user.username  = msg.from_user.username
        user.name      = data.get("name")
        user.tz        = data.get("tz")
        user.goal      = data.get("goal")
        user.exp_level = int(data.get("exp") or 0)
        user.consent_at= datetime.utcnow()
        s.add(user); s.commit()
    await state.clear()
    await msg.answer("Готово. Добро пожаловать в меню.", reply_markup=main_menu())
