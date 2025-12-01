from __future__ import annotations

from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

router = Router(name="api")


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """
    Базовая команда /start для бота.
    Здесь можно будет подключать настоящее меню,
    когда решим, что HQ-бот должен уметь.
    """
    await message.answer(
        "Привет. Я — бот Элайи.\n"
        "Я запущен и готов к работе. "
        "Основная логика тренера живёт в отдельном сервисе, "
        "но я уже на связи."
    )


@router.message(Command("ping"))
async def cmd_ping(message: Message) -> None:
    """
    Простая проверка живости бота.
    """
    await message.answer("pong")
