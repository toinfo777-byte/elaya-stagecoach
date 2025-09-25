# app/keyboards/common.py
from aiogram.utils.keyboard import InlineKeyboardBuilder

def menu_btn():
    kb = InlineKeyboardBuilder()
    kb.button(text="🏠 В меню", callback_data="go:menu")
    return kb.as_markup()
