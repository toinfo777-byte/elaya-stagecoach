from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router(name="scene_reflect")

@router.message(Command("scene_reflect"))
async def reflect_scene(message: Message):
    text = (
        "🪞 Рефлексия сцены.\n"
        "Сделай мягкий выдох и отметь главное различение.\n"
        "Один факт • одно чувство • одно решение."
    )
    await message.answer(text)
