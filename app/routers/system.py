# app/routers/system.py
from __future__ import annotations
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

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
    "/health — проверка статуса\n"
)

PRIVACY_TEXT = (
    "<b>Политика</b>\n\n"
    "Мы храним минимум данных, необходимые для работы тренера и подсчёта прогресса. "
    "Команда <code>/wipe_me</code> удалит профиль и записи. "
    "Подробная политика — ваша ссылка/текст."
)

@router.message(Command("help"))
async def help_cmd(m: Message):
    await m.answer(HELP_TEXT)

@router.message(Command("privacy"))
async def privacy_cmd(m: Message):
    await m.answer(PRIVACY_TEXT)
