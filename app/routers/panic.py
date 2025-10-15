from aiogram import Router, F
from aiogram.types import Message

router = Router(name="panic")

@router.message(F.text.in_({"/panic", "panic"}))
async def panic_cmd(message: Message):
    raise RuntimeError("🔥 Sentry test: manual /panic")
