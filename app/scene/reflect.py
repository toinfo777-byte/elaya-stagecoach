from aiogram import Router
from aiogram.types import Message
from .manager import scene_manager

router = Router(name="scene_reflect")

@router.message(commands=["scene_reflect"])
async def reflect_scene(message: Message):
    cfg = scene_manager.get_config("scene_reflect")
    hint = f"⏱ окно: ~{cfg.duration_sec//60} мин • время в штабе: {cfg.time}" if cfg else ""
    text = (
        "🌕 Отрази свой день.\n"
        "Что сегодня было светлым?\n"
        "Какая мысль или жест остались с тобой?\n"
        f"{hint}"
    )
    await message.answer(text)
