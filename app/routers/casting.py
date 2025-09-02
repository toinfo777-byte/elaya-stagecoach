# app/routers/casting.py
from __future__ import annotations
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from app.keyboards.menu import main_menu
from app.storage.repo import session_scope
from app.storage.models import User, Test, TestResult
from app.services.scoring import questions, score_answers, recommend_drills

router = Router(name="casting")

class CastingFlow(StatesGroup):
    q = State()  # спрашиваем по одному
    done = State()

def _q_kb(opts: list[str]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=opt, callback_data=f"opt::{i}")] for i, opt in enumerate(opts)
    ])

@router.message(StateFilter("*"), F.text == "🎭 Мини-кастинг")
@router.message(StateFilter("*"), Command("casting"))
async def start_casting(m: Message, state: FSMContext):
    with session_scope() as s:
        u = s.query(User).filter_by(tg_id=m.from_user.id).first()
        if not u:
            await m.answer("Сначала /start для онбординга.", reply_markup=main_menu())
            return
        # один раз положим тест в БД, если пусто
        if s.query(Test).count() == 0:
            s.add(Test(id="basic10", payload_json={"count": len(questions())}))
            s.commit()

    await state.update_data(idx=0, answers={})
    await state.set_state(CastingFlow.q)
    q = questions()[0]
    await m.answer(f"Вопрос 1/10:\n{q.text}", reply_markup=_q_kb(q.options))

@router.callback_query(CastingFlow.q, F.data.startswith("opt::"))
async def handle_answer(cb: CallbackQuery, state: FSMContext):
    d = await state.get_data()
    idx: int = int(d.get("idx", 0))
    ans: dict = d.get("answers", {})

    qs = questions()
    q = qs[idx]
    i = int(cb.data.split("::", 1)[1])
    choice = q.options[i]
    ans[q.id] = choice

    idx += 1
    if idx >= len(qs):
        # конец — считаем профиль
        axes = score_answers(ans)
        total = sum(axes.values())
        with session_scope() as s:
            u = s.query(User).filter_by(tg_id=cb.from_user.id).first()
            if u:
                s.add(TestResult(user_id=u.id, axes_json=axes, score_total=total))
                s.commit()
        # рекомендации
        rec_ids = recommend_drills(axes)
        if rec_ids:
            rec_txt = "Рекомендации на завтра: " + ", ".join(f"`{r}`" for r in rec_ids)
        else:
            rec_txt = "Рекомендации: продолжайте текущие этюды."
        axes_txt = (
            f"Внимание: {axes['attention']} | Пауза: {axes['pause']} | "
            f"Темп: {axes['tempo']} | Интонация: {axes['intonation']} | Логика: {axes['logic']}"
        )
        await state.clear()
        await cb.message.edit_text("Готово. Профиль различения собран.")
        await cb.message.answer(axes_txt + "\n" + rec_txt, reply_markup=main_menu(), parse_mode=None)
        await cb.answer()
        return

    # иначе следующий вопрос
    await state.update_data(idx=idx, answers=ans)
    q = qs[idx]
    await cb.message.edit_text(f"Вопрос {idx+1}/10:\n{q.text}", reply_markup=_q_kb(q.options))
    await cb.answer()
