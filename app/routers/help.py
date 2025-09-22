# app/routers/help.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from app.keyboards.menu import main_menu, BTN_HELP

router = Router(name="help")

HELP = (
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
)


@router.message(Command("help"))
@router.message(F.text == BTN_HELP)
async def help_cmd(msg: Message):
    await msg.answer(HELP, reply_markup=main_menu())
