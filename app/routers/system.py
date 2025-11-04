from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command

from app.build import BUILD_MARK

router = Router(name="system")

MENU_TEXT = (
    "Команды и разделы: выбери нужное 🧭\n\n"
    "🏋️ Тренировка дня — ежедневная рутина 5–15 мин.\n"
    "📈 Мой прогресс — стрики и эпизоды за 7 дней.\n"
    "🎯 Мини-кастинг • 🧭 Путь лидера\n"
    "🆘 Помощь / FAQ • ⚙️ Настройки\n"
    "📜 Политика • ⭐ Расширенная версия"
)

@router.message(CommandStart())
async def cmd_start(msg: Message):
    await msg.answer(MENU_TEXT)

@router.message(Command("healthz"))
async def cmd_healthz(msg: Message):
    await msg.answer("ok")

@router.message(Command("menu"))
async def cmd_menu(msg: Message):
    await msg.answer(MENU_TEXT)

@router.message(Command("help"))
async def cmd_help(msg: Message):
    await msg.answer(
        "Помощь:\n"
        "• /menu — показать главное меню\n"
        "• /status — статус ядра и билд\n"
        "• /webhookinfo — параметры вебхука\n"
        "• /healthz — быстрая проверка\n"
        "• ping — быстрый echo-пинг (текстом)\n"
        f"\nBuild: <code>{BUILD_MARK}</code>"
    )
