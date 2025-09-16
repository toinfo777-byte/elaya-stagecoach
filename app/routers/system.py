from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.types import Message

from app.routers.menu import main_menu, BTN_HELP, BTN_PRIVACY

router = Router(name="system")

HELP_TEXT = (
    "*Помощь*\n\n"
    "Команды:\n"
    "/start — начать и онбординг\n"
    "/menu — открыть меню\n"
    "/apply — Путь лидера (заявка)\n"
    "/training — тренировка дня\n"
    "/casting — мини-кастинг\n"
    "/progress — мой прогресс\n"
    "/privacy — политика конфиденциальности\n"
    "/version — версия бота\n"
    "/health — проверка статуса\n"
    "/cancel — сбросить состояние\n"
)
PRIVACY_TEXT = (
    "🔐 *Политика конфиденциальности*\n\n"
    "Мы храним минимум данных и используем их только для работы бота. "
    "Команда /wipe_me удалит профиль и связанные записи."
)

@router.message(StateFilter("*"), Command("help"))
async def cmd_help(m: Message):
    await m.answer(HELP_TEXT, parse_mode="Markdown", reply_markup=main_menu())

@router.message(StateFilter("*"), Command("privacy"))
async def cmd_privacy(m: Message):
    await m.answer(PRIVACY_TEXT, parse_mode="Markdown", reply_markup=main_menu())

# Кнопки из меню
@router.message(StateFilter("*"), lambda x: x.text == BTN_HELP)
async def btn_help(m: Message):
    await cmd_help(m)

@router.message(StateFilter("*"), lambda x: x.text == BTN_PRIVACY)
async def btn_privacy(m: Message):
    await cmd_privacy(m)

@router.message(StateFilter("*"), Command("version"))
async def cmd_version(m: Message):
    await m.answer("version=dev tmp")

@router.message(StateFilter("*"), Command("health"))
async def cmd_health(m: Message):
    await m.answer("OK")
