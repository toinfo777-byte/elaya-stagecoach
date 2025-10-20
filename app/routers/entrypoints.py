# app/routers/entrypoints.py
from aiogram import Router, types, F
from aiogram.filters import CommandStart, Command

router = Router()

# /start → показать главное меню
@router.message(CommandStart())
async def cmd_start(msg: types.Message):
    await msg.answer(
        "Команды и разделы: выбери нужное 🧭\n"
        "🏋️ Тренировка дня — ежедневная рутина 5–15 мин.\n"
        "📈 Мой прогресс — стрик и эпизоды за 7 дней.\n"
        "🎯 Мини-кастинг · 💥 Путь лидера\n"
        "❓ Помощь / FAQ · ⚙️ Настройки\n"
        "🧭 Политика · ⭐ Расширенная версия"
    )

# Явные команды, если хочешь здесь же продублировать меню по /menu
@router.message(Command("menu"))
async def cmd_menu(msg: types.Message):
    await cmd_start(msg)

# Фоллбек на любой текст: без фильтра ~Command()
# (не используем ~Command() вообще)
@router.message(F.text)
async def any_text(msg: types.Message):
    await cmd_start(msg)
