# app/routers/trainer.py
from __future__ import annotations
import os, aiohttp
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

router = Router(name="trainer")

CORE_API_BASE = os.getenv("CORE_API_BASE", "").rstrip("/")
CORE_API_TOKEN = os.getenv("CORE_API_TOKEN", "")


async def _post_scene(path: str, payload: dict) -> str:
    if not CORE_API_BASE:
        return "⚠️ Портал спит. Настрой адрес ядра."
    url = f"{CORE_API_BASE}{path}"
    headers = {"X-Core-Token": CORE_API_TOKEN} if CORE_API_TOKEN else {}
    try:
        async with aiohttp.ClientSession() as s:
            async with s.post(url, json=payload, headers=headers, timeout=15) as r:
                if r.status != 200:
                    return "⚠️ Сейчас тихо. Повтори позже."
                data = await r.json()
                return data.get("reply", "…")
    except Exception:
        return "⚠️ Портал перегружается. Попробуй ещё раз."


@router.message(Command("start"))
async def cmd_start(m: Message):
    reply = await _post_scene("/api/scene/enter", {
        "user_id": m.from_user.id, "chat_id": m.chat.id, "text": None, "scene": "intro"
    })
    await m.answer("Меню тренировки:\n" + reply)


@router.message(Command("scene_intro"))
async def scene_intro(m: Message):
    reply = await _post_scene("/api/scene/enter", {
        "user_id": m.from_user.id, "chat_id": m.chat.id, "text": None, "scene": "intro"
    })
    await m.answer(reply)


@router.message(Command("scene_reflect"))
async def scene_reflect(m: Message):
    reply = await _post_scene("/api/scene/reflect", {
        "user_id": m.from_user.id, "chat_id": m.chat.id, "text": None, "scene": "reflect"
    })
    await m.answer(reply)


@router.message(Command("scene_transition"))
async def scene_transition(m: Message):
    reply = await _post_scene("/api/scene/transition", {
        "user_id": m.from_user.id, "chat_id": m.chat.id, "text": None, "scene": "transition"
    })
    await m.answer(reply)


@router.message(F.text & ~F.via_bot)
async def any_text(m: Message):
    reply = await _post_scene("/api/scene/reflect", {
        "user_id": m.from_user.id, "chat_id": m.chat.id, "text": m.text, "scene": "reflect"
    })
    await m.answer(reply)
