# app/bot/handlers/feedback.py
from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from app.bot.states import Feedback
from app.bot.keyboards.feedback import rating_kb, skip_kb
from app.bot.keyboards.main_menu import main_menu_kb  # если есть свой — используй его импорт

# твои функции работы с БД (из того файла, который ты прислал)
from app.storage.db import session_scope, log_event

router = Router()

# ВЫЗОВ СПРОСИТЬ ОТЗЫВ — подставь свой триггер/место, где это уместно
@router.message(F.text == "/ask_review")
async def ask_review(msg: Message, state: FSMContext):
    await state.set_state(Feedback.WaitRating)
    await msg.answer(
        "Как прошёл этюд? Оцените или оставьте краткий отзыв:",
        reply_markup=rating_kb()
    )

# ПОЛУЧАЕМ ОЦЕНКУ (кнопки 🔥/👌/😐 или переход к тексту)
@router.callback_query(F.data.startswith("rate:"), Feedback.WaitRating)
async def on_rating(cb: CallbackQuery, state: FSMContext):
    action = cb.data.split(":", 1)[1]
    tg_id = cb.from_user.id

    if action == "text":
        # Переключаемся на ввод текста
        await state.set_state(Feedback.WaitText)
        # убираем старые inline-кнопки, чтобы не нажимали второй раз
        await cb.message.edit_reply_markup(reply_markup=None)
        await cb.message.answer("Напишите 1 фразу о впечатлении:", reply_markup=skip_kb())
        await cb.answer()
        return

    # Оценки и «Пропустить» с шага WaitRating
    rating = {"hot": "🔥", "ok": "👌", "meh": "😐", "skip": "skip"}.get(action, "skip")

    # Логируем, но не ломаем поток, если что-то пойдёт не так
    try:
        with session_scope() as s:
            log_event(s, user_id=None, name="rating", payload={"tg_id": tg_id, "rating": rating})
    except Exception:
        pass

    await cb.message.edit_reply_markup(reply_markup=None)
    await cb.answer("Сохранено")
    await state.clear()
    await cb.message.answer("Спасибо! Что дальше?", reply_markup=main_menu_kb())

# ТЕКСТОВЫЙ ОТЗЫВ
@router.message(Feedback.WaitText)
async def on_text_review(msg: Message, state: FSMContext):
    tg_id = msg.from_user.id
    text = (msg.text or "").strip()

    if text:
        try:
            with session_scope() as s:
                log_event(s, user_id=None, name="review_text", payload={"tg_id": tg_id, "text": text})
        except Exception:
            pass

    await state.clear()
    await msg.answer("Спасибо! Учтено ✅", reply_markup=main_menu_kb())

# «ПРОПУСТИТЬ» на шаге текстового отзыва
@router.callback_query(F.data == "rate:skip", Feedback.WaitText)
async def on_skip_text(cb: CallbackQuery, state: FSMContext):
    await cb.answer("Пропущено")
    await state.clear()
    await cb.message.edit_reply_markup(reply_markup=None)
    await cb.message.answer("Спасибо! Что дальше?", reply_markup=main_menu_kb())

# МЕНЮ ДОЛЖНО РАБОТАТЬ ИЗ ЛЮБОГО СОСТОЯНИЯ — перехватываем кнопки меню
@router.message(
    StateFilter("*"),
    F.text.in_({"🏋️ Тренировка дня", "📈 Мой прогресс", "🧭 Путь лидера", "🎭 Мини-кастинг", "🗣 Помощь"})
)
async def menu_any_state(msg: Message, state: FSMContext):
    # сбрасываем зависшее состояние
    await state.clear()
    # здесь сделай переходы на свои сценарии; базово просто показываем меню
    await msg.answer("Готово. Вы в главном меню.", reply_markup=main_menu_kb())
