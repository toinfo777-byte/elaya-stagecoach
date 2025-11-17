from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Тексты кнопок главного меню — в константах,
# чтобы при необходимости можно было переиспользовать в роутерах.
BTN_TRAINING = "🏋️‍♂️ Тренировка дня"
BTN_PROGRESS = "📈 Мой прогресс"
BTN_HELP = "💬 Помощь"
BTN_POLICY = "🔐 Политика"
BTN_PRO = "⭐️ Расширенная версия"

MAIN_MENU = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=BTN_TRAINING)],
        [
            KeyboardButton(text=BTN_PROGRESS),
            KeyboardButton(text=BTN_HELP),
        ],
        [
            KeyboardButton(text=BTN_POLICY),
            KeyboardButton(text=BTN_PRO),
        ],
    ],
    resize_keyboard=True,
    input_field_placeholder="Команды и разделы: выбери нужное ⤵️",
)
