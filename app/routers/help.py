# app/routers/help.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message

from app.keyboards.reply import main_menu_kb, BTN_HELP

router = Router(name="help")

HELP_TEXT = (
    "Команды:\n"
    "/start — начать\n"
    "/menu — меню\n"
    "/training — тренировка\n"
    "/casting — мини-кастинг\n"
    "/progress — мой прогресс\n"
    "/apply — путь лидера\n"
    "/privacy — политика\n"
    "/help — помощь\n"
    "/settings — настройки\n"
    "/extended — расширенная версия"
)


@router.message(Command("help"), StateFilter(None))
@router.message(F.text == BTN_HELP, StateFilter(None))
async def help_cmd(m: Message):
    await m.answer(HELP_TEXT, reply_markup=main_menu_kb())
