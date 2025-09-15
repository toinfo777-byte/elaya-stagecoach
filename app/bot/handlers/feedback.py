from __future__ import annotations

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import SkipHandler

from app.bot.states import FeedbackStates

router = Router(name="feedback2")

# ----- Кнопки «оценить/фраза» -----
def feedback_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔥", callback_data="fb:rate:hot"),
            InlineKeyboardButton(text="👌", callback_data="fb:rate:good"),
            InlineKeyboardButton(text="😐", callback_data="fb:rate:meh"),
        ],
        [InlineKeyboardButton(text="✍ 1 фраза", callback_data="fb:phrase")],
    ])

# Вспомогательно: набор текстов «нижних» кнопок, чтобы их не блокировать в состоянии отзыва
PASS_THROUGH_TEXTS: set[str] = {
    "Меню", "Тренировка дня", "Мой прогресс", "Путь лидера",
    "Мини-кастинг", "Политика", "Настройки", "Расширенная версия",
    "Удалить профиль", "Помощь",
}

# ===== Хэндлеры =====

# 1) Оценка-эмодзи — показываем тост "Ок" и благодарим. Состояние НЕ включаем.
@router.callback_query(F.data.startswith("fb:rate:"))
async def on_rate(cb: CallbackQuery, state: FSMContext) -> None:
    # короткий тост (без всплывающего окна)
    await cb.answer("Ок")
    # здесь можно логировать/сохранять оценку (cb.from_user.id, cb.data)
    await cb.message.answer("Спасибо! Принял 👍")
    # состояние не трогаем — ничего не блокируется

# 2) «✍ 1 фраза» — просим текст и переходим в состояние ожидания фразы
@router.callback_query(F.data == "fb:phrase")
async def on_phrase_start(cb: CallbackQuery, state: FSMContext) -> None:
    await cb.answer()
    await state.set_state(FeedbackStates.wait_phrase)
    await cb.message.answer(
        "Напишите коротко (1–2 предложения). "
        "Если передумали — нажмите любую кнопку меню внизу или /cancel."
    )

# 3) Пришёл текст от пользователя — сохраняем и выходим из состояния
@router.message(FeedbackStates.wait_phrase, F.text)
async def phrase_received(msg: Message, state: FSMContext) -> None:
    text = (msg.text or "").strip()

    # Если человек нажал «нижнюю кнопку» или набрал команду — снимаем состояние и пропускаем дальше
    if text in PASS_THROUGH_TEXTS or text.startswith("/"):
        await state.clear()
        raise SkipHandler  # важно: разрешаем обработать это другими роутерами (меню и т.д.)

    # Лёгкая валидация
    if len(text) < 2:
        await msg.answer("Чуть подробнее, пожалуйста 🙂")
        return
    if len(text) > 600:
        await msg.answer("Получилось длинновато. Сократите, пожалуйста, до 1–2 предложений.")
        return

    # TODO: сохранить отзыв (msg.from_user.id, text) в БД/метрики
    await state.clear()
    await msg.answer("Спасибо за отзыв! 💛")

# 4) Нечитаемый контент в состоянии отзыва (стикер/голос и т.п.)
@router.message(FeedbackStates.wait_phrase)
async def phrase_non_text(msg: Message, state: FSMContext) -> None:
    await msg.answer("Мне нужен короткий текст. Можете также выйти в меню любой кнопкой внизу.")
