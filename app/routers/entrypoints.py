from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ChatType

router = Router(name="entrypoints")

# /start — только приват
@router.message(Command("start"), F.chat.type == ChatType.PRIVATE)
async def cmd_start(m: Message) -> None:
    await m.answer(
        "Команды и разделы: выбери нужное 🧭\n"
        "🏅 Тренировка дня — ежедневная рутина 5–15 мин.\n"
        "📈 Мой прогресс — стрик и эпизоды за 7 дней.\n"
        "🧪 Мини-кастинг · 🧭 Путь лидера\n"
        "💬 Помощь / FAQ · ⚙️ Настройки\n"
        "🔐 Политика · ⭐️ Расширенная версия"
    )

# /menu — только приват
@router.message(Command("menu"), F.chat.type == ChatType.PRIVATE)
async def cmd_menu(m: Message) -> None:
    await m.answer(
        "Команды и разделы: выбери нужное 🧭\n"
        "🏅 Тренировка дня — ежедневная рутина 5–15 мин.\n"
        "📈 Мой прогресс — стрик и эпизоды за 7 дней.\n"
        "🧪 Мини-кастинг · 🧭 Путь лидера\n"
        "💬 Помощь / FAQ · ⚙️ Настройки\n"
        "🔐 Политика · ⭐️ Расширенная версия"
    )

# защита от случайных триггеров: в группах меню/старт игнорируются,
# этим занимается мидлварь GroupGate + фильтры выше.
