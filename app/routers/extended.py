from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from app.texts.strings import EXTENDED_TEXT
from app.keyboards.menu import main_menu

router = Router(name="extended")

@router.message(Command("extended"))
async def ext_cmd(m: Message):
    await m.answer(EXTENDED_TEXT, reply_markup=main_menu())
