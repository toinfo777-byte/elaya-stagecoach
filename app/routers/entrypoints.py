# app/routers/entrypoints.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from app.routers.help import show_main_menu

router = Router(name="entrypoints")


@router.message(F.text.in_({"/start", "start"}))
async def cmd_start(msg: Message):
    await show_main_menu(msg)


@router.message(F.text.in_({"/menu", "menu"}))
async def cmd_menu(msg: Message):
    await show_main_menu(msg)


@router.callback_query(F.data == "go:menu")
async def go_menu(cb: CallbackQuery):
    await show_main_menu(cb)
