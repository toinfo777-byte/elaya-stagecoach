from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, BotCommand

# Константы главного меню
BTN_TRAINING = "🎯 Тренировка дня"
BTN_APPLY = "🧭 Путь лидера"
BTN_PRIVACY = "🔐 Политика"
BTN_PREMIUM = "⭐ Расширенная версия"
BTN_PROGRESS = "📈 Мой прогресс"
BTN_CASTING = "🎭 Мини-кастинг"
BTN_HELP = "💬 Помощь"
BTN_SETTINGS = "⚙️ Настройки"

# Маленькое меню (reply)
BTN_TO_MENU = "🏠 В меню"
BTN_TO_SETTINGS = "⚙️ Настройки"
BTN_WIPE = "🗑 Удалить профиль"

def main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_TRAINING), KeyboardButton(text=BTN_PROGRESS)],
            [KeyboardButton(text=BTN_APPLY), KeyboardButton(text=BTN_CASTING)],
            [KeyboardButton(text=BTN_PRIVACY), KeyboardButton(text=BTN_HELP)],
            [KeyboardButton(text=BTN_SETTINGS), KeyboardButton(text=BTN_PREMIUM)],
        ],
        resize_keyboard=True,
        input_field_placeholder="Меню",
    )

def small_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_TO_MENU), KeyboardButton(text=BTN_TO_SETTINGS)],
            [KeyboardButton(text=BTN_WIPE)],
        ],
        resize_keyboard=True,
    )

def get_bot_commands() -> list[BotCommand]:
    return [
        BotCommand(command="start", description="Запуск / онбординг"),
        BotCommand(command="menu", description="Открыть меню"),
        BotCommand(command="training", description="Тренировка"),
        BotCommand(command="progress", description="Мой прогресс"),
        BotCommand(command="apply", description="Путь лидера"),
        BotCommand(command="casting", description="Мини-кастинг"),
        BotCommand(command="privacy", description="Политика конфиденциальности"),
        BotCommand(command="help", description="Помощь"),
        BotCommand(command="settings", description="Настройки"),
        BotCommand(command="cancel", description="Отменить текущее действие"),
        BotCommand(command="wipe_me", description="Удалить профиль"),
    ]
