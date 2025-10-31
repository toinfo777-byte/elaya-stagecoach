from __future__ import annotations

import os
import time
from aiogram import Router, F, types
from aiogram.filters import Command

router = Router(name="hq")

# Этот роутер разрешаем и в приват, и в группах (глобальный фильтр private в main.py
# НЕ действует на него, потому что тут мы вешаем свои фильтры локально).
router.message.filter(F.chat.type.in_({"private", "group", "supergroup"}))

START_TS = time.time()


def _uptime() -> str:
    s = int(time.time() - START_TS)
    h, r = divmod(s, 3600)
    m, _ = divmod(r, 60)
    return f"{h}h {m}m"


@router.message(Command("hq"))
async def hq_summary(msg: types.Message) -> None:
    env = os.getenv("ENV", "staging")
    mode = os.getenv("MODE", "webhook")
    build = os.getenv("BUILD_SHA", "unknown")
    sha = os.getenv("RENDER_GIT_COMMIT", "unknown")
    uptime = _uptime()

    text = (
        "<b>🧭 HQ-сводка</b>\n"
        f"• Bot: <code>ENV={env} MODE={mode} BUILD={build} SHA={sha}</code>\n"
        f"• Uptime: <code>{uptime}</code>\n"
    )
    await msg.answer(text)


@router.message(Command("healthz"))
async def healthz_cmd(msg: types.Message) -> None:
    await msg.answer("ok ✅")
