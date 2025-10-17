# app/routers/entrypoints.py
from aiogram import Router, types
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

router = Router(name="entrypoints")

@router.message(CommandStart())
async def start(m: types.Message, state: FSMContext):
    await show_main_menu(m)

@router.message(Command("menu"))
async def menu(m: types.Message):
    await show_main_menu(m)

# ⬇️ ВАЖНО: этот обработчик только для НЕ-команд
@router.message(~Command())
async def any_text_fallback(m: types.Message):
    await show_main_menu(m)

async def show_main_menu(m: types.Message):
    await m.answer(
        "Команды и разделы: выбери нужное 🧭\n\n"
        "🏋️ Тренировка дня — ежедневная рутина 5–15 мин.\n"
        "📈 Мой прогресс — стрик и эпизоды за 7 дней.\n"
        "💥 Мини-кастинг · 🛰️ Путь лидера\n"
        "🆘 Помощь / FAQ · ⚙️ Настройки\n"
        "📜 Политика · ⭐ Расширенная версия"
    )
