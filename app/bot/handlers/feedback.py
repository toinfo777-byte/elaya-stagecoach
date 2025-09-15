from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from app.bot.states import FeedbackStates

router = Router(name="feedback2")

# Клавиатура оценок
def feedback_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔥", callback_data="fb:rate:hot"),
            InlineKeyboardButton(text="👌", callback_data="fb:rate:good"),
            InlineKeyboardButton(text="😐", callback_data="fb:rate:meh"),
        ],
        [InlineKeyboardButton(text="✍ 1 фраза", callback_data="fb:phrase")],
    ])

# 1) Оценка-эмодзи
@router.callback_query(F.data.startswith("fb:rate:"))
async def on_rate(cb: CallbackQuery, state: FSMContext) -> None:
    try:
        await cb.answer("Ок")
    except Exception:
        pass
    await cb.message.answer("Спасибо! Принял 👍")

# 2) Запрос «✍ 1 фраза»
@router.callback_query(F.data == "fb:phrase")
async def on_phrase_start(cb: CallbackQuery, state: FSMContext) -> None:
    try:
        await cb.answer()
    except Exception:
        pass
    await state.set_state(FeedbackStates.wait_phrase)
    await cb.message.answer(
        "Напишите коротко (1–2 предложения).\n"
        "Если передумали — можно просто нажать любую кнопку внизу или отправить /menu."
    )

# Разрешённые «нижние» кнопки/команды, чтобы не мешать меню
PASS_THROUGH_TEXTS = {
    "Меню", "Тренировка дня", "Мой прогресс", "Путь лидера",
    "Мини-кастинг", "Политика", "Настройки", "Расширенная версия",
    "Удалить профиль", "Помощь",
}

# 3) Принять фразу
@router.message(FeedbackStates.wait_phrase, F.text)
async def phrase_received(msg: Message, state: FSMContext) -> None:
    text = (msg.text or "").strip()

    # Если пользователь нажал «нижнюю кнопку» или ввёл команду — просто очищаем состояние и
    # НИЧЕГО не отвечаем: обработают другие роутеры (меню и т.п.).
    if text in PASS_THROUGH_TEXTS or text.startswith("/"):
        await state.clear()
        return

    if len(text) < 2:
        await msg.answer("Чуть подробнее, пожалуйста 🙂")
        return
    if len(text) > 600:
        await msg.answer("Получилось длинновато. Сократите, пожалуйста, до 1–2 предложений.")
        return

    # TODO: здесь сохраните отзыв в БД/метрики
    await state.clear()
    await msg.answer("Спасибо за отзыв! 💛")

# 4) Нечитаемое в состоянии отзыва
@router.message(FeedbackStates.wait_phrase)
async def phrase_non_text(msg: Message, state: FSMContext) -> None:
    await msg.answer("Нужен короткий текст. Или нажмите любую кнопку внизу, чтобы выйти.")
