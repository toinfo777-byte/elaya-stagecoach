from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router(name="scene_intro")

@router.message(Command("scene_intro"))
async def intro_scene(message: Message):
    text = (
        "🌅 Добро пожаловать на внутреннюю сцену Элайи.\n"
        "Вдох — настрой, внимание, присутствие.\n"
        "Дыши в унисон со светом."
    )
    await message.answer(text)
