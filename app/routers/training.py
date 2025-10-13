from __future__ import annotations
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

router = Router(name="training")

ENTRY_TEXTS = {
    "🏋️ тренировка дня", "тренировка дня", "training", "уровень 1",
}

@router.message(Command("training"))
@router.message(F.text.casefold().in_(ENTRY_TEXTS))
async def training_entry(m: Message):
    # Простой, но «законченный» сценарий: сразу выдаём тренировку дня
    await m.answer(
        "✨ <b>Тренировка дня</b>\n\n"
        "1) Встань. Почувствуй опору стоп.\n"
        "2) 5 спокойных вдохов/выдохов. На вдохе — внимание в сердце, на выдохе — в мир.\n"
        "3) Произнеси вслух короткую фразу текста (любую). Сохраняй мягкий тембр.\n"
        "4) Повтори 3 минуты.\n\n"
        "✅ Когда завершишь — вернись в меню: /menu"
    )

# 🔁 ШИМ ДЛЯ СОВМЕСТИМОСТИ СО СТАРЫМ КОДОМ
# Раньше cmd_aliases импортировал show_training_levels — вернём имя.
async def show_training_levels(m: Message):
    # Просто переиспользуем текущую точку входа
    await training_entry(m)

__all__ = ["router", "training_entry", "show_training_levels"]
