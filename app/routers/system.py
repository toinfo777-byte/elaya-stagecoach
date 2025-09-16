from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from app.routers.menu import BTN_HELP, BTN_PRIVACY, main_menu

router = Router(name="system")

PRIVACY_TEXT = (
    "🔐 *Политика конфиденциальности*\n\n"
    "Мы храним минимум данных: ваш Telegram ID и ответы внутри бота.\n"
    "Командой /wipe_me профиль и ваши записи можно удалить."
)

HELP_TEXT = (
    "💬 *Помощь*\n\n"
    "Команды:\n"
    "/start — начать и онбординг\n"
    "/menu — открыть меню\n"
    "/apply — Путь лидера (заявка)\n"
    "/training — тренировка дня\n"
    "/casting — мини-кастинг\n"
    "/progress — мой прогресс\n"
    "/privacy — политика конфиденциальности\n"
    "/version — версия бота\n"
    "/cancel — сбросить состояние\n"
)

@router.message(Command("help"))
@router.message(F.text == BTN_HELP)
async def help_handler(m: Message):
    await m.answer(HELP_TEXT, parse_mode="Markdown", reply_markup=main_menu())

@router.message(Command("privacy"))
@router.message(F.text == BTN_PRIVACY)
async def privacy_handler(m: Message):
    await m.answer(PRIVACY_TEXT, parse_mode="Markdown", reply_markup=main_menu())

@router.message(Command("version"))
async def version_handler(m: Message):
    await m.answer("version=dev tmp", reply_markup=main_menu())

@router.message(Command("menu"))
async def menu_handler(m: Message):
    await m.answer("Меню", reply_markup=main_menu())
