from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from app.keyboards.menu import main_menu

router = Router(name="help")

HELP_TEXT = (
    "Помощь:\n\n"
    "• 🎯 *Тренировка дня* — короткий этюд + рефлексия\n"
    "• 🎭 *Мини-кастинг* — 8–10 пунктов, соберём профиль различения\n"
    "• 📈 *Мой прогресс* — стрик, последние этюды и твой профиль 5 осей\n"
    "• ⚙️ *Настройки* — удалить профиль (/wipe_me)\n"
    "• ⭐ *Расширенная версия* — персональные треки и мини-группа\n"
)

@router.message(F.text == "💬 Помощь")
@router.message(Command("help"))
async def help_cmd(m: Message):
    await m.answer(HELP_TEXT, parse_mode="Markdown", reply_markup=main_menu())
