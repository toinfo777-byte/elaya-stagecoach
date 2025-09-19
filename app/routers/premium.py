# app/routers/premium.py
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder

router = Router(name="premium")

# Кнопки для подменю
def premium_menu() -> types.ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="ℹ️ Что внутри")
    kb.button(text="📋 Мои заявки")
    kb.button(text="📎 В меню")
    return kb.as_markup(resize_keyboard=True)


@router.message(Command("premium"))
@router.message(lambda m: m.text == "⭐️ Расширенная версия")
async def premium_entry(message: types.Message):
    text = (
        "⭐️ <b>Расширенная версия</b>\n\n"
        "• Ежедневный разбор и обратная связь\n"
        "• Разогрев голоса, дикции и внимания\n"
        "• Мини-кастинг и путь лидера\n\n"
        "Выберите действие:"
    )
    await message.answer(text, reply_markup=premium_menu())


@router.message(lambda m: m.text == "ℹ️ Что внутри")
async def premium_info(message: types.Message):
    await message.answer("📦 Внутри расширенной версии — больше практики и персональных разборов.")


@router.message(lambda m: m.text == "📋 Мои заявки")
async def premium_list(message: types.Message):
    # TODO: подключить базу, пока просто заглушка
    await message.answer("Заявок пока нет.")


@router.message(lambda m: m.text == "📎 В меню")
async def premium_back(message: types.Message):
    from app.keyboards.menu import main_menu
    await message.answer("Ок, вернулись в главное меню. Нажми нужную кнопку снизу.", reply_markup=main_menu())
