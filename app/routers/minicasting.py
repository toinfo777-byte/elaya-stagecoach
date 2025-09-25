# app/routers/minicasting.py
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.storage.repo_extras import save_casting_session, save_feedback
from app.keyboards.reply import main_menu_kb, BTN_CASTING
from app.keyboards.inline import mc_feedback_kb

router = Router(name="minicasting")

class MiniCasting(StatesGroup):
    q = State()
    answers = State()
    feedback = State()

QUESTIONS = [
    "Удержал ли 2 сек тишины перед фразой? (Да/Нет)",
    "Голос после паузы звучал ровнее? (Да/Нет)",
    "Что было труднее? (Пауза/Тембр/То же)",
    "Лёгкость дыхания по ощущениям? (Да/Нет)",
    "Хочешь повторить круг сейчас? (Да/Нет)",
]

def yn_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="Да", callback_data="mini:yes")
    kb.button(text="Нет", callback_data="mini:no")
    kb.button(text="Дальше", callback_data="mini:next")
    kb.button(text="В меню", callback_data="mini:menu")
    kb.adjust(2, 2)
    return kb.as_markup()

async def _start_minicasting_core(msg: Message, state: FSMContext):
    await state.set_state(MiniCasting.q)
    await state.update_data(q=0, answers=[])
    await msg.answer("Это мини-кастинг: 2–3 мин. Отвечай коротко. Готов?", reply_markup=yn_kb())

@router.message(F.text == BTN_CASTING)
async def start_minicasting(msg: Message, state: FSMContext):
    await _start_minicasting_core(msg, state)

@router.message(StateFilter("*"), Command("casting"))
async def start_minicasting_cmd(msg: Message, state: FSMContext):
    await _start_minicasting_core(msg, state)

@router.callback_query(F.data.startswith("mini:"), MiniCasting.q)
async def on_answer(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    q = data["q"]
    answers = data["answers"]

    if cb.data == "mini:menu":
        await state.clear()
        await cb.message.answer("Готово! Открываю меню.", reply_markup=main_menu_kb())
        return await cb.answer()

    if cb.data in {"mini:yes", "mini:no"}:
        answers.append(cb.data.split(":")[1])

    q += 1
    if q <= len(QUESTIONS):
        await state.update_data(q=q, answers=answers)
        await cb.message.edit_text(QUESTIONS[q-1], reply_markup=yn_kb())
        return await cb.answer()

    # итог
    tip = "Точка роста: не давай паузе проваливаться." if answers[:2].count("no") >= 1 else "Отлично! Держи курс и темп."
    await cb.message.edit_text(f"Итог: {tip}")
    await cb.message.answer("Оцени опыт 🔥/👌/😐 и добавь 1 слово-ощущение (необязательно).", reply_markup=mc_feedback_kb())
    await state.set_state(MiniCasting.feedback)
    try:
        await save_casting_session(cb.from_user.id, answers=answers, result=("pause" if "no" in answers[:2] else "ok"))
    except Exception:
        pass
    await cb.answer()

# Пропуск отзыва
@router.callback_query(F.data == "mc:skip", StateFilter(MiniCasting.feedback, MiniCasting.q))
async def mc_skip(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.message.answer("Ок, вернёмся завтра. Возвращаю в меню.", reply_markup=main_menu_kb())
    await cb.answer()

# Эмодзи (совместимо с текущими fb:* payload'ами)
@router.callback_query(F.data.startswith("fb:"), MiniCasting.feedback)
async def on_fb_emoji(cb: CallbackQuery, state: FSMContext):
    # fb:fire | fb:ok | fb:meh  (не эмодзи-сам символ, а код)
    emoji_code = cb.data.split(":", 1)[1]
    mapping = {"fire": "🔥", "ok": "👌", "meh": "😐"}
    emoji = mapping.get(emoji_code, "👌")
    try:
        await save_feedback(cb.from_user.id, emoji=emoji, phrase=None)
    except Exception:
        pass
    await cb.message.answer("Принял. Можешь одним словом дописать ощущение (до 140 симв) или нажми «В меню».")
    await cb.answer()

# Любой текст — сохраняем и в меню
@router.message(MiniCasting.feedback)
async def on_fb_phrase(msg: Message, state: FSMContext):
    phrase = (msg.text or "").strip()[:140] if msg.text else ""
    try:
        await save_feedback(msg.from_user.id, emoji="👌", phrase=phrase or None)
    except Exception:
        pass
    await state.clear()
    await msg.answer("Спасибо! Записал. Возвращаю в меню.", reply_markup=main_menu_kb())
