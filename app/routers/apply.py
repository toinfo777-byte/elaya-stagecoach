# app/routers/apply.py
from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router(name="apply")

# Тексты, по которым триггеримся (кнопка меню может слать просто текст)
TEXT_TRIGGERS = {
    "путь лидера",
    "🧭 путь лидера",
    "путь лидера (заявка)",
    "заявка путь лидера",
}

ASK_TEXT = (
    "Путь лидера — индивидуальная траектория с фокусом на цели.\n"
    "Оставьте заявку — вернусь с вопросами и предложениями.\n\n"
    "<i>Напишите цель одной короткой фразой (до 200 символов). Если передумали — отправьте /cancel.</i>"
)

CONFIRM_TEXT = "Спасибо! Принял. Двигаемся дальше 👍"

# Вход — команда
@router.message(Command("apply"))
async def apply_cmd(message: Message) -> None:
    await message.answer(ASK_TEXT)

# Вход — нажатие текстовой кнопки в меню
@router.message(F.text.casefold().in_(t.lower() for t in TEXT_TRIGGERS))
async def apply_text(message: Message) -> None:
    await message.answer(ASK_TEXT)

# Примитивное «сохранение заявки»: любое текстовое сообщение,
# пришедшее после вопроса, считаем заявкой (на простом слое).
# Если у вас есть состояние/БД — подмените на свою логику.
@router.message(F.text & ~Command())
async def apply_save(message: Message) -> None:
    text = (message.text or "").strip()
    # Отфильтруем служебные строки меню, чтобы не ловить их как заявку
    if text.casefold() in {"/menu", "/start", "/training", "/progress", "/casting", "/premium", "/settings"}:
        return
    # Примитивная валидация: 200 символов
    if len(text) > 200:
        await message.answer("Слишком длинно. Сформулируйте цель до 200 символов.")
        return

    # TODO: сохранить в вашу БД, если есть
    # repo.save_leader_apply(user_id=message.from_user.id, goal=text)

    await message.answer(CONFIRM_TEXT)
    # После подтверждения — в главное меню (кнопка внизу у вас уже есть)
