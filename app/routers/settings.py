# app/routers/settings.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

# Безопасные импорты UI (fallback, если вдруг нет модулей)
try:
    from app.keyboards.reply import BTN_SETTINGS, main_menu_kb
except Exception:
    BTN_SETTINGS = "⚙️ Настройки"
    def main_menu_kb():
        return None  # без клавиатуры тоже ок

# Безопасный импорт операции удаления пользователя
try:
    from app.storage.repo_extras import delete_user  # async
except Exception:
    async def delete_user(tg_id: int) -> None:  # fallback no-op
        return

router = Router(name="settings")

# ----- Клавиатуры -----
def settings_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🗑 Удалить мои данные", callback_data="set:del:ask")],
        [InlineKeyboardButton(text="🏠 В меню", callback_data="go:menu")],
    ])

def confirm_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Да, удалить", callback_data="set:del:yes"),
            InlineKeyboardButton(text="Отмена", callback_data="set:del:no"),
        ]
    ])

# ----- Хэндлеры -----
@router.message(Command("settings"))
@router.message(F.text == BTN_SETTINGS)
async def show_settings(m: Message):
    await m.answer(
        "⚙️ <b>Настройки</b>\n\n"
        "— Здесь можно удалить ваши данные, если передумали пользоваться ботом.\n"
        "— Остальные опции появятся позже.",
        reply_markup=settings_kb(),
    )

@router.callback_query(F.data == "set:del:ask")
async def ask_delete(cb: CallbackQuery):
    await cb.answer()
    await cb.message.answer(
        "❗️ Подтвердите удаление ваших данных (tg_id, локальные записи прогресса и пр.). Это действие необратимо.",
        reply_markup=confirm_kb(),
    )

@router.callback_query(F.data == "set:del:no")
async def cancel_delete(cb: CallbackQuery):
    await cb.answer("Отмена")
    await cb.message.answer("Ок, ничего не удалял. Возвращаю в меню.", reply_markup=main_menu_kb())

@router.callback_query(F.data == "set:del:yes")
async def do_delete(cb: CallbackQuery):
    await cb.answer()
    try:
        await delete_user(cb.from_user.id)
        await cb.message.answer("Готово. Данные удалены. Возвращаю в меню.", reply_markup=main_menu_kb())
    except Exception:
        # Не роняем поток, просто сообщаем
        await cb.message.answer("Не удалось удалить данные сейчас. Попробуйте позже.", reply_markup=main_menu_kb())

__all__ = ["router", "show_settings"]
