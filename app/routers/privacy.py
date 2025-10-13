# app/routers/privacy.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

# Безопасные импорты кнопки и клавиатуры
try:
    from app.keyboards.reply import BTN_PRIVACY, main_menu_kb
except Exception:
    BTN_PRIVACY = "🔐 Политика"
    def main_menu_kb():
        return None

router = Router(name="privacy")

PRIVACY_TEXT = (
    "🔐 <b>Политика конфиденциальности</b>\n\n"
    "Мы сохраняем минимум данных, необходимых для работы бота:\n"
    "• ваш Telegram ID для идентификации;\n"
    "• служебные события тренировки для расчёта прогресса.\n\n"
    "Мы не передаём персональные данные третьим лицам. "
    "Для удаления профиля используйте раздел «⚙️ Настройки» → «Удалить профиль»."
)

@router.message(Command("privacy"))
async def cmd_privacy(m: Message) -> None:
    await m.answer(PRIVACY_TEXT, reply_markup=main_menu_kb())

@router.message(F.text == BTN_PRIVACY)
async def btn_privacy(m: Message) -> None:
    await m.answer(PRIVACY_TEXT, reply_markup=main_menu_kb())

# Алиас на всякий случай
privacy_router = router

__all__ = ["router", "privacy_router"]
