# app/routers/settings.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from app.keyboards.reply import main_menu_kb
from app.storage.repo_extras import delete_user  # stub – уже есть

router = Router(name="settings")

def settings_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🗑 Удалить мои данные")],
            [KeyboardButton(text="🏠 В меню")],
        ],
        resize_keyboard=True
    )

@router.message(Command("settings"))
@router.message(StateFilter("*"), F.text == "⚙️ Настройки")
async def settings_home(msg: Message):
    await msg.answer(
        "⚙️ <b>Настройки</b>\n\n"
        "— Здесь можно удалить ваши данные, если передумали пользоваться ботом.\n"
        "— Остальные опции появятся позже.",
        reply_markup=settings_kb()
    )

@router.message(StateFilter("*"), F.text == "🗑 Удалить мои данные")
async def settings_delete(msg: Message):
    await delete_user(msg.from_user.id)  # stub: просто логирует
    await msg.answer("Ок, запись помечена на удаление (заглушка).", reply_markup=main_menu_kb())

@router.message(StateFilter("*"), F.text == "🏠 В меню")
async def back_home(msg: Message):
    await msg.answer("Вернул в меню.", reply_markup=main_menu_kb())
