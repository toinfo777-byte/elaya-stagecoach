from __future__ import annotations

from aiogram import F, Router
from aiogram.types import Message

router = Router()

# ─────────────────────────────────────────────────────────────────────────────
# ГЛУШИТЕЛЬ: в группах пропускаем ВСЁ, что не начинается с '/' (не команда)
# ─────────────────────────────────────────────────────────────────────────────
@router.message(F.chat.type.in_({"group", "supergroup"}) & ~F.text.startswith("/"))
async def _ignore_non_commands(_: Message) -> None:
    return


# Ниже — твои обычные команды. Ничего не менял, только оставил примеры.
@router.message(F.text.as_("t") & F.text.startswith("/ping"))
async def cmd_ping(m: Message, t: str) -> None:
    await m.reply("pong")

@router.message(F.text.as_("t") & F.text.startswith("/status"))
async def cmd_status(m: Message, t: str) -> None:
    await m.reply("✅ Я на месте. Webhook online.")

@router.message(F.text.as_("t") & F.text.startswith("/hq"))
async def cmd_hq(m: Message, t: str) -> None:
    # тут оставь свою сборку «штабного» блока/клавиатуры
    await m.reply("Команды и разделы: выбери нужное ⚙️")
