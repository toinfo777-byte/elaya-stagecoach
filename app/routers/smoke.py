# app/routers/smoke.py
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from app.config import settings

router = Router(name="smoke")

@router.message(Command("ping"))
async def ping(m: Message):
    await m.answer("pong")

@router.message(Command("health"))
async def health(m: Message):
    await m.answer(f"ok | env={settings.env} | db=sqlite | uptime=n/a")

@router.message(Command("whoami"))
async def whoami(m: Message):
    await m.answer(f"id={m.from_user.id} | chat={m.chat.id}")

@router.message(Command("version"))
async def version(m: Message):
    # не делаем здесь проверку на админа — просто, чтобы был ответ
    await m.answer("version=dev tmp")
