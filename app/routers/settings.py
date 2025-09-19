from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from app.storage.repo import session_scope, delete_user_cascade
from app.storage.models import User
from app.keyboards.menu import main_menu, BTN_SETTINGS

router = Router(name="settings")

def kb_settings() -> ReplyKeyboardMarkup:
    rows = [
        [KeyboardButton(text="🗑 Удалить профиль")],
        [KeyboardButton(text="📣 В меню")],
    ]
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True, is_persistent=True)

@router.message(Command("settings"))
@router.message(F.text == BTN_SETTINGS)
async def settings_entry(message: Message) -> None:
    await message.answer(
        "⚙️ Настройки.\nМожешь удалить профиль или вернуться в меню.",
        reply_markup=kb_settings(),
    )

@router.message(F.text == "🗑 Удалить профиль")
async def settings_wipe(message: Message) -> None:
    with session_scope() as s:
        u = s.query(User).filter_by(tg_id=message.from_user.id).first()
        if not u:
            await message.answer("Профиль не найден.")
        else:
            ok = delete_user_cascade(s, user_id=u.id)
            await message.answer("Готово. Данные удалены." if ok else "Не получилось удалить. Попробуй позже.")
    await message.answer("Возвращаю в меню.", reply_markup=main_menu())

@router.message(F.text.in_({"📣 В меню", "В меню"}))
async def settings_back(message: Message) -> None:
    await message.answer("Ок, вернулись в главное меню. Нажми нужную кнопку снизу.", reply_markup=main_menu())
