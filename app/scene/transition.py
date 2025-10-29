from aiogram import Router
from aiogram.types import Message

router = Router(name="scene_transition")

@router.message(commands=["scene_transition"])
async def transition_scene(message: Message):
    text = (
        "🌄 Сделай шаг в следующий день.\n"
        "Выдох — и действие.\n"
        "Пусть всё, что ты понял, станет движением."
    )
    await message.answer(text)
