from aiogram import Router
from aiogram.types import Message

router = Router(name="scene_reflect")

@router.message(commands=["scene_reflect"])
async def reflect_scene(message: Message):
    text = (
        "🌕 Отрази свой день.\n"
        "Что сегодня было светлым?\n"
        "Какая мысль или жест остались с тобой?"
    )
    await message.answer(text)
