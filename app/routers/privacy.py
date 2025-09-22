# app/routers/privacy.py
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

# аккуратно тянем кнопки/меню; если константы переименованы — подставим дефолт
try:
    from app.keyboards.menu import main_menu, BTN_PRIVACY
except Exception:
    from app.keyboards.menu import main_menu  # type: ignore
    BTN_PRIVACY = "🔐 Политика"

router = Router(name="privacy")

PRIVACY_TEXT = (
    "Политика конфиденциальности: мы бережно храним ваши данные и "
    "используем их только для работы бота.\n\n"
    "Подробнее: https://example.com/privacy"
)

@router.message(Command("privacy"))
@router.message(F.text == BTN_PRIVACY)  # нажали кнопку «Политика»
async def show_privacy(msg: Message):
    await msg.answer(PRIVACY_TEXT, reply_markup=main_menu())
