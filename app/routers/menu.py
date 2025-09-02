from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from app.keyboards.menu import main_menu
from app.texts.strings import HELP

router = Router(name="menu")

@router.message(Command("menu"))
async def menu_cmd(msg: Message):
    await msg.answer("Меню:", reply_markup=main_menu())

@router.message(Command("help"))
async def help_cmd(msg: Message):
    await msg.answer(HELP, reply_markup=main_menu())

@router.message(F.text == "💬 Помощь")
async def help_btn(msg: Message):
    await msg.answer(HELP, reply_markup=main_menu())
