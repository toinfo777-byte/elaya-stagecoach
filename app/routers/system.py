from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.filters import CommandStart, Command

from app.build import BUILD_MARK
from app.config import settings

router = Router(name="system")

MENU_TEXT = (
    "Команды и разделы: выбери нужное 🧭\n\n"
    "🏋️ Тренировка дня — ежедневная рутина 5–15 мин.\n"
    "📈 Мой прогресс — стрики и эпизоды за 7 дней.\n"
    "🎯 Мини-кастинг • 🧭 Путь лидера\n"
    "🆘 Помощь / FAQ • ⚙️ Настройки\n"
    "📜 Политика • ⭐ Расширенная версия"
)

def trainer_menu() -> ReplyKeyboardMarkup:
    """Клавиатура доступна только в профиле 'trainer'."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🏋️ Тренировка дня"), KeyboardButton(text="📈 Мой прогресс")],
            [KeyboardButton(text="🎯 Путь лидера"), KeyboardButton(text="⚙️ Настройки")],
            [KeyboardButton(text="🆘 Помощь / FAQ"), KeyboardButton(text="⭐ Расширенная версия")],
            [KeyboardButton(text="📜 Политика")],
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
    )

@router.message(CommandStart())
async def cmd_start(msg: Message):
    if settings.BOT_PROFILE == "trainer":
        await msg.answer(MENU_TEXT, reply_markup=trainer_menu())
    else:
        # штаб: никаких меню
        await msg.answer(
            f"🟢 HQ online\nBuild: <code>{BUILD_MARK}</code>",
            reply_markup=ReplyKeyboardRemove(),
        )

@router.message(Command("healthz"))
async def cmd_healthz(msg: Message):
    await msg.answer("ok", reply_markup=ReplyKeyboardRemove())

@router.message(Command("menu"))
async def cmd_menu(msg: Message):
    if settings.BOT_PROFILE == "trainer":
        await msg.answer(MENU_TEXT, reply_markup=trainer_menu())
    else:
        await msg.answer("Меню недоступно в HQ-профиле.", reply_markup=ReplyKeyboardRemove())

@router.message(Command("help"))
async def cmd_help(msg: Message):
    await msg.answer(
        "Помощь:\n"
        "• /menu — показать главное меню (только trainer)\n"
        "• /status — статус ядра и билд\n"
        "• /webhookinfo — параметры вебхука\n"
        "• /healthz — быстрая проверка\n"
        "• ping — быстрый echo-пинг (текстом)\n"
        f"\nBuild: <code>{BUILD_MARK}</code>",
        reply_markup=ReplyKeyboardRemove(),
    )

# На всякий случай: любой текст «ping» — ответ без клавиатуры,
# чтобы не залипала даже при тестах
@router.message(F.text == "ping")
async def ping(msg: Message):
    await msg.answer("pong", reply_markup=ReplyKeyboardRemove())
