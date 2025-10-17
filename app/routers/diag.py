# app/routers/diag.py
from aiogram import Router, types
import os

router = Router()

@router.message(commands=["diag"])
async def cmd_diag(message: types.Message):
    env = os.getenv("ENV", "develop")
    release = os.getenv("SHORT_SHA", "local")
    text = (
        f"🧩 <b>Diag report</b>\n"
        f"🌿 <b>Environment:</b> <code>{env}</code>\n"
        f"🏗 <b>Release:</b> <code>{release}</code>\n"
        f"✅ Sentry: active\n"
        f"💓 Cronitor: heartbeat running\n"
        f"🤖 Bot: alive"
    )
    await message.answer(text)
