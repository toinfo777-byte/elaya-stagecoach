# app/routers/system.py
from __future__ import annotations
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from app.routers.menu import main_menu

router = Router(name="system")

HELP_TEXT = (
    "<b>Помощь</b>\n\n"
    "Команды:\n"
    "/start — начать и онбординг\n"
    "/menu — открыть меню\n"
    "/apply — Путь лидера (заявка)\n"
    "/training — тренировка дня\n"
    "/casting — мини-кастинг\n"
    "/progress — мой прогресс\n"
    "/cancel — сбросить состояние\n"
    "/privacy — политика конфиденциальности\n"
    "/version — версия бота\n"
    "/health — проверка статуса"
)

PRIVACY_TEXT = "🔐 Политика конфиденциальности… (ваш текст)."

@router.message(Command("help"))
async def help_cmd(m: Message):
    await m.answer(HELP_TEXT, reply_markup=main_menu())

@router.message(Command("privacy"))
async def privacy_cmd(m: Message):
    await m.answer(PRIVACY_TEXT, reply_markup=main_menu())
