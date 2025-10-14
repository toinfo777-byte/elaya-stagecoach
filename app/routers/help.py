# app/routers/help.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router(name="help")


def build_main_menu():
    """
    Единая inline-клавиатура для главного меню.
    Её будем переиспользовать из других роутеров.
    """
    kb = InlineKeyboardBuilder()
    kb.button(text="🔁 Обновить меню", callback_data="go:menu")
    kb.button(text="🛠 Диагностика",  callback_data="go:diag")
    kb.button(text="❓ Помощь",       callback_data="go:help")
    kb.adjust(2, 1)
    return kb.as_markup()


async def show_main_menu(target: Message | CallbackQuery):
    """
    Унифицированный вывод главного меню.
    Принимает Message или CallbackQuery, чтобы удобно вызывать из разных мест.
    """
    text = (
        "Команды и разделы: выбери нужное 🎯\n\n"
        "• /menu — главное меню\n"
        "• /levels — список тренировок\n"
        "• /progress — мой прогресс\n"
        "• /help — помощь / FAQ\n"
        "• /diag — диагностика сборки"
    )

    reply_markup = build_main_menu()
    # Если пришли из callback — отвечаем в тот же чат
    if isinstance(target, CallbackQuery):
        # закрываем кружочек “loading”
        await target.answer()
        await target.message.answer(text, reply_markup=reply_markup)
    else:
        await target.answer(text, reply_markup=reply_markup)


@router.message(F.text.in_({"/help", "help"}))
async def cmd_help(msg: Message):
    """Команда /help — краткая справка + кнопки меню."""
    help_text = (
        "🆘 <b>Помощь / FAQ</b>\n\n"
        "• /menu — главное меню\n"
        "• /levels — список тренировок\n"
        "• /progress — ваш прогресс\n"
        "• /ping — проверка связи\n"
        "• /diag — сведения о версии (для отладки)\n\n"
        "Если что-то не работает — напишите здесь же, посмотрим."
    )
    await msg.answer(help_text, reply_markup=build_main_menu())


@router.callback_query(F.data == "go:help")
async def go_help(cb: CallbackQuery):
    """Кнопка “Помощь” из меню."""
    await cmd_help(cb.message)
