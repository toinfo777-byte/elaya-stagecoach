from aiogram import Router
from aiogram.types import Message

router = Router(name="debug")

# универсальный эхо-хэндлер (на время диагностики).
@router.message()
async def echo_all(m: Message):
    # отвечаем только в личке, чтобы в группах не спамить
    if m.chat.type in ("private",):
        await m.answer(f"🔁 Эхо: {m.text}")
