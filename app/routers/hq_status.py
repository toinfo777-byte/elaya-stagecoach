# app/routers/hq_status.py
from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router(name="hq_status")

@router.message(Command("ping"))
async def cmd_ping(m: Message):
    await m.reply("pong")

@router.message(Command("status"))
async def cmd_status(m: Message):
    await m.reply("✅ HQ online (webhook)")

@router.message(Command("healthz"))
async def cmd_healthz(m: Message):
    await m.reply("200 OK")
