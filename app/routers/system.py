# app/routers/system.py
from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

# Если у тебя есть объект настроек с версией — импортируй его.
# from app.config import settings

router = Router(name="system")

HELP_TEXT = (
    "💬 *Помощь*\n\n"
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
    "🔒 *Политика конфиденциальности*\n\n"
    "Мы бережно относимся к вашим данным и используем их только для работы бота "
    "и улучшения качества сервиса."
)

@router.message(Command("help"))
async def cmd_help(m: Message) -> None:
    await m.answer(HELP_TEXT, parse_mode="Markdown")

@router.message(Command("privacy"))
async def cmd_privacy(m: Message) -> None:
    await m.answer(PRIVACY_TEXT, parse_mode="Markdown")

@router.message(Command("version"))
async def cmd_version(m: Message) -> None:
    # Если есть settings.app_version — раскомментируй строку ниже и замени текст
    # await m.answer(f"🤖 Версия бота: {settings.app_version}")
    await m.answer("🤖 Версия бота: beta")

@router.message(Command("health"))
async def cmd_health(m: Message) -> None:
    await m.answer("✅ OK")
