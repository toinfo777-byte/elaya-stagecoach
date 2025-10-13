# app/routers/privacy.py
from __future__ import annotations
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from app.keyboards.reply import main_menu_kb, BTN_PRIVACY

router = Router(name="privacy")

@router.message(Command("privacy"))
@router.message(F.text == BTN_PRIVACY)
async def privacy(m: Message):
    await m.answer(
        "🔐 Политика конфиденциальности (кратко):\n— Мы не продаём и не передаём ваши данные.\n— Храним минимум, нужный для работы тренера.\n— Запрос на удаление: в Настройках.\n\n(полный текст будет по ссылке позже)",
        reply_markup=main_menu_kb()
    )
