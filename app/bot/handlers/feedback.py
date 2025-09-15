# app/bot/handlers/feedback.py
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from app.bot.states import FeedbackStates
from app.bot.ui.feedback import build_feedback_kb, send_feedback_prompt

router = Router(name="feedback2")

# ==== ХЕЛПЕРЫ СХЕМЫ СОХРАНЕНИЯ (пока — в память FSM; при желании смените на БД) ====

async def _save_reaction(user_id: int, kind: str) -> None:
    # TODO: замените на реальную запись в БД/метрики
    # пример: repo.feedback.add_reaction(user_id=user_id, kind=kind)
    pass

async def _save_phrase(user_id: int, text: str) -> None:
    # TODO: замените на реальную запись в БД/метрики
    # пример: repo.feedback.add_phrase(user_id=user_id, text=text)
    pass


# ==== ПОКАЗ КЛАВИАТУРЫ «ГДЕ УГОДНО» (для команд/кнопок, если понадобится) ====

@router.message(F.text == "/feedback")   # опционально: команда чтобы вызвать блок вручную
async def feedback_entry(msg: Message):
    await send_feedback_prompt(msg)


# ==== ОБРАБОТЧИКИ КНОПОК ОЦЕНКИ ====

@router.callback_query(F.data.in_({"fb:hot", "fb:ok", "fb:meh"}))
async def on_feedback_reaction(cb: CallbackQuery):
    kind_map = {"fb:hot": "hot", "fb:ok": "ok", "fb:meh": "meh"}
    kind = kind_map.get(cb.data)
    await _save_reaction(cb.from_user.id, kind)
    await cb.answer("Сохранено ✅", show_alert=False)

@router.callback_query(F.data == "fb:phrase")
async def on_feedback_phrase(cb: CallbackQuery, state: FSMContext):
    await cb.answer()  # закрыть «часики»
    await cb.message.answer("Напишите короткую фразу-отзыв одним сообщением (до 200 символов).")
    await state.set_state(FeedbackStates.wait_phrase)


# ==== ПРИЁМ «1 ФРАЗЫ» ====

@router.message(FeedbackStates.wait_phrase, F.text)
async def on_feedback_phrase_text(msg: Message, state: FSMContext):
    text = (msg.text or "").strip()
    if not text:
        await msg.answer("Пусто 🤔 Напишите короткую фразу (можно одним-двумя предложениями).")
        return
    if len(text) > 200:
        await msg.answer("Давайте короче (до 200 символов), пожалуйста 🙂")
        return

    await _save_phrase(msg.from_user.id, text)
    await state.clear()
    await msg.answer("Спасибо! Сохранил отзыв ✍️")

# на всякий случай: если пришёл не текст — напомним
@router.message(FeedbackStates.wait_phrase)
async def on_feedback_phrase_nontext(msg: Message):
    await msg.answer("Нужен обычный текст 🙂 Напишите короткую фразу-отзыв.")
