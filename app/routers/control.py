from __future__ import annotations

from aiogram import Router
from aiogram.types import Message

router = Router(name="control_safe")

# ВАЖНО: никаких импортов из app.control.* — чтобы не ронять сервис.
# Если позже появится полноценный модуль контроля — просто заменим реализацию.


@router.message(commands={"control", "ctl"})
async def control_stub(msg: Message) -> None:
    await msg.answer(
        "🛡️ Блок *control* временно отключён.\n"
        "Импорты admin/ops вычищены, чтобы не ронять воркеры.\n"
        "Когда будет готов модуль управления, подменим заглушку.",
        parse_mode="Markdown",
    )
