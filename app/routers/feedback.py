# app/routers/feedback.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from app.storage.repo import session_scope, log_event
from app.storage import models as models_module
from app.storage.models import User

router = Router(name="feedback")

# Опциональная модель Feedback (если есть в проекте)
FeedbackModel = getattr(models_module, "Feedback", None)

# Эмодзи, которые часто шлют как «быструю оценку» в мобильной версии
QUICK_EMOJIS = {"🔥", "👌", "😐", "👍", "👎", "🙂", "🙁"}

class FeedbackFlow(StatesGroup):
    waiting_text = State()  # ждём текст отзыва


@dataclass
class FBContext:
    scope: str
    ref_id: str
    rating: Optional[str] = None  # строкой — поддержим и цифры, и эмодзи


# ===== Команда /feedback =====
@router.message(StateFilter("*"), Command("feedback"))
async def start_feedback_cmd(m: Message, state: FSMContext):
    await state.set_state(FeedbackFlow.waiting_text)
    await state.update_data(fb=FBContext(scope="free", ref_id="manual").__dict__)
    await m.answer("Напишите короткий отзыв (1–2 фразы). Чтобы отменить — /cancel")


# ===== Обработка КОЛЛБЭКОВ с клавиатуры =====
# Раньше было строго \d+ — расширим на любой не-двоеточечный маркер рейтинга
# Формат ожидаем такой: fb:<scope>:<ref_id>:rate:<mark>
@router.callback_query(StateFilter("*"), F.data.regexp(r"^fb:[^:]+:[^:]+:rate:[^:]+$"))
async def fb_rate(cb: CallbackQuery, state: FSMContext):
    try:
        _, scope, ref_id, _, mark = cb.data.split(":")
    except Exception:
        await cb.answer()
        return

    with session_scope() as s:
        u = s.query(User).filter_by(tg_id=cb.from_user.id).first()
        if u:
            # метрика
            try:
                log_event(s, u.id, "feedback_added", {"scope": scope, "ref_id": ref_id, "rating": mark})
                s.commit()
            except Exception:
                pass

            # запись в Feedback (если модель есть)
            if FeedbackModel is not None:
                try:
                    fb = FeedbackModel(user_id=u.id, scope=scope, ref_id=str(ref_id), rating=mark, text=None)
                    s.add(fb)
                    s.commit()
                except Exception:
                    pass

    await cb.message.answer("Спасибо! Оценка сохранена. Если хотите — пришлите короткий текст отзывом.")
    await cb.answer()


# fb:<scope>:<ref_id>:write → ждём текст
@router.callback_query(StateFilter("*"), F.data.regexp(r"^fb:[^:]+:[^:]+:write$"))
async def fb_write(cb: CallbackQuery, state: FSMContext):
    try:
        _, scope, ref_id, _ = cb.data.split(":")
    except Exception:
        await cb.answer()
        return

    await state.set_state(FeedbackFlow.waiting_text)
    await state.update_data(fb=FBContext(scope=scope, ref_id=ref_id).__dict__)
    await cb.message.answer("Напишите 1–2 фразы отзывом. Чтобы отменить — /cancel")
    await cb.answer()


# ===== Принимаем ТЕКСТ отзыва =====
@router.message(FeedbackFlow.waiting_text, F.text)
async def fb_text(m: Message, state: FSMContext):
    data = await state.get_data()
    ctx = data.get("fb") or {}
    scope = ctx.get("scope", "free")
    ref_id = ctx.get("ref_id", "manual")
    rating = ctx.get("rating")

    text = (m.text or "").strip()
    if not text:
        await m.answer("Пришлите текст отзыва или /cancel для отмены.")
        return

    with session_scope() as s:
        u = s.query(User).filter_by(tg_id=m.from_user.id).first()
        if u:
            # метрика
            try:
                log_event(s, u.id, "feedback_added", {"scope": scope, "ref_id": ref_id, "rating": rating, "text": text})
                s.commit()
            except Exception:
                pass

            # запись в Feedback (если модель есть)
            if FeedbackModel is not None:
                try:
                    fb = FeedbackModel(user_id=u.id, scope=scope, ref_id=str(ref_id), rating=rating, text=text)
                    s.add(fb)
                    s.commit()
                except Exception:
                    pass

    await state.clear()
    await m.answer("Спасибо! Отзыв сохранён 🙌")


# ===== Фолбэки под телефон: быстрые оценки эмодзи и «✍️ 1 фраза» текстом =====
@router.message(StateFilter("*"), F.text.in_(QUICK_EMOJIS))
async def fb_quick_emoji(m: Message):
    # когда эмодзи прилетает обычным текстом без callback_data
    mark = (m.text or "").strip()
    with session_scope() as s:
        u = s.query(User).filter_by(tg_id=m.from_user.id).first()
        if u:
            try:
                log_event(s, u.id, "feedback_added", {"scope": "manual", "ref_id": "None", "rating": mark})
                s.commit()
            except Exception:
                pass
    await m.answer("Спасибо! Оценка сохранена.")


@router.message(StateFilter("*"), F.text == "✍️ 1 фраза")
async def fb_one_phrase(m: Message, state: FSMContext):
    await state.set_state(FeedbackFlow.waiting_text)
    await state.update_data(fb=FBContext(scope="manual", ref_id="None").__dict__)
    await m.answer("Напишите 1–2 фразы. Чтобы отменить — /cancel")
