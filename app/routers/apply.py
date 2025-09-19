# app/routers/apply.py
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder

router = Router(name="apply")

# Кнопки для подменю
def apply_menu() -> types.ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="✍️ Оставить заявку")
    kb.button(text="📋 Мои заявки")
    kb.button(text="📎 В меню")
    return kb.as_markup(resize_keyboard=True)


@router.message(Command("apply"))
@router.message(lambda m: m.text == "🧭 Путь лидера")
async def apply_entry(message: types.Message):
    text = (
        "🧭 <b>Путь лидера</b> — индивидуальная траектория с фокусом на цели.\n\n"
        "Оставьте заявку — вернусь с вопросами и предложениями."
    )
    await message.answer(text, reply_markup=apply_menu())


@router.message(lambda m: m.text == "✍️ Оставить заявку")
async def apply_new(message: types.Message):
    await message.answer(
        "✍️ Путь лидера: короткая заявка.\n"
        "Напишите, чего хотите достичь — одним сообщением (до 200 символов).\n"
        "Если передумали — /cancel."
    )


@router.message(lambda m: m.text == "📋 Мои заявки")
async def apply_list(message: types.Message):
    # TODO: подключить базу, пока просто заглушка
    await message.answer("Заявок пока нет.")


@router.message(lambda m: m.text == "📎 В меню")
async def apply_back(message: types.Message):
    from app.keyboards.menu import main_menu
    await message.answer("Ок, вернулись в главное меню. Нажми нужную кнопку снизу.", reply_markup=main_menu())
