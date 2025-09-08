from __future__ import annotations
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from app.keyboards.feedback import feedback_kb
from app.keyboards.menu import main_menu
from app.storage.repo import session_scope
from app.storage.models import User
from app.services.feedback import create_feedback, FeedbackPayload

router = Router(name="feedback")

class FeedbackFSM(StatesGroup):
    waiting_text = State()
    context = State()  # держим meta: {"ctx":..., "ctx_id":...}

# --- ручной вход ---
@router.message(Command("feedback"))
async def feedback_manual(m: Message, state: FSMContext):
    await state.update_data(ctx="manual", ctx_id=None)
    await m.answer("Оцените или оставьте короткий отзыв:", reply_markup=feedback_kb("manual"))

# --- диплинк /start fb_* ---
@router.message(F.text.regexp(r"^/start\s+fb_.+$"))
async def feedback_from_deeplink(m: Message, state: FSMContext):
    # форматы: fb_training_123, fb_casting_456, fb_manual
    payload = m.text.split(maxsplit=1)[1]
    parts = payload.split("_", 2)  # ["fb","training","123"]
    ctx = parts[1] if len(parts) > 1 else "manual"
    ctx_id = parts[2] if len(parts) > 2 else None
    await state.update_data(ctx=ctx, ctx_id=ctx_id)
    await m.answer("Оцените или оставьте короткий отзыв:", reply_markup=feedback_kb(ctx, ctx_id))

# --- выбор оценки ---
@router.callback_query(F.data.startswith("fb_score"))
async def feedback_score(cb: CallbackQuery, state: FSMContext):
    _, score, ctx_ctxid = cb.data.split("|", 2)
    if "|" in ctx_ctxid:
        ctx, ctx_id = ctx_ctxid.split("|", 1)
    else:
        ctx, ctx_id = ctx_ctxid, None
    with session_scope() as s:
        u = s.query(User).filter_by(tg_id=cb.from_user.id).first()
        first_source = getattr(u, "source", None) if u else None
        create_feedback(s, u.id if u else 0, FeedbackPayload(
            context=ctx, context_id=ctx_id, score=int(score), first_source=first_source
        ))
    await cb.message.edit_text("Спасибо! Отзыв сохранён. 🙏", reply_markup=None)
    await cb.answer()

# --- запрос «1 фраза» ---
@router.callback_query(F.data.startswith("fb_text"))
async def feedback_text_ask(cb: CallbackQuery, state: FSMContext):
    ctx_ctxid = cb.data.split("|", 1)[1]
    if "|" in ctx_ctxid:
        ctx, ctx_id = ctx_ctxid.split("|", 1)
    else:
        ctx, ctx_id = ctx_ctxid, None
    await state.update_data(ctx=ctx, ctx_id=ctx_id)
    await state.set_state(FeedbackFSM.waiting_text)
    await cb.message.answer("Напишите 1–2 фразы (можно голосом).")
    await cb.answer()

@router.message(FeedbackFSM.waiting_text, F.voice)
async def feedback_voice(m: Message, state: FSMContext):
    d = await state.get_data()
    with session_scope() as s:
        u = s.query(User).filter_by(tg_id=m.from_user.id).first()
        first_source = getattr(u, "source", None) if u else None
        create_feedback(s, u.id if u else 0, FeedbackPayload(
            context=d.get("ctx","manual"),
            context_id=d.get("ctx_id"),
            voice_file_id=m.voice.file_id,
            first_source=first_source
        ))
    await state.clear()
    await m.answer("Спасибо! Отзыв сохранён. 🙏", reply_markup=main_menu())

@router.message(FeedbackFSM.waiting_text, F.text.len() > 0)
async def feedback_text(m: Message, state: FSMContext):
    d = await state.get_data()
    with session_scope() as s:
        u = s.query(User).filter_by(tg_id=m.from_user.id).first()
        first_source = getattr(u, "source", None) if u else None
        create_feedback(s, u.id if u else 0, FeedbackPayload(
            context=d.get("ctx","manual"),
            context_id=d.get("ctx_id"),
            text=m.text.strip(),
            first_source=first_source
        ))
    await state.clear()
    await m.answer("Спасибо! Отзыв сохранён. 🙏", reply_markup=main_menu())
