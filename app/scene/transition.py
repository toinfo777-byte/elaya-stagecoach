from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router(name="scene_transition")

@router.message(Command("scene_transition"))
async def transition_scene(message: Message):
    text = (
        "🌗 Переход.\n"
        "Собери внимание в звезду груди и перенеси его в следующий шаг.\n"
        "Сохрани ритм дыхания Элайи."
    )
    await message.answer(text)
