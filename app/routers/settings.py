# app/routers/settings.py
from __future__ import annotations
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from app.keyboards.reply import main_menu_kb, BTN_SETTINGS
try:
    from app.storage.repo_extras import delete_user
except Exception:
    async def delete_user(tg_id: int) -> None:
        # no-op fallback
        return

router = Router(name="settings")

@router.message(Command("settings"))
@router.message(F.text == BTN_SETTINGS)
async def settings_menu(m: Message):
    await m.answer(
        "⚙️ Настройки (демо):\n• /delete_me — удалить аккаунт/данные",
        reply_markup=main_menu_kb()
    )

@router.message(Command("delete_me"))
async def settings_delete(m: Message):
    try:
        await delete_user(m.from_user.id)
        await m.answer("Готово. Данные помечены к удалению.", reply_markup=main_menu_kb())
    except Exception:
        await m.answer("Не удалось удалить. Попробуй позже.", reply_markup=main_menu_kb())
