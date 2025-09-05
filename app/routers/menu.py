from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from app.keyboards.menu import main_menu
from app.texts.strings import HELP
from app.routers.system import PRIVACY_TEXT  # берём текст политики из system.py

router = Router(name="menu")


@router.message(Command("menu"))
async def menu_cmd(msg: Message):
    await msg.answer("Меню:", reply_markup=main_menu())


# /help и кнопка «Помощь»
@router.message(Command("help"))
@router.message(F.text == "💬 Помощь")
async def help_msg(msg: Message):
    await msg.answer(HELP, reply_markup=main_menu())


# Политика (кнопка и любые тексты где встречается «политик»)
@router.message(F.text.in_({"🔐 Политика", "Политика"}))
@router.message(lambda m: isinstance(m.text, str) and "политик" in m.text.lower())
async def privacy_msg(msg: Message):
    await msg.answer(PRIVACY_TEXT, reply_markup=main_menu())
