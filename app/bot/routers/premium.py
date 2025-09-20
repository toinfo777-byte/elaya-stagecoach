from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from app.bot.keyboards.menu import premium_kb, main_menu_kb

router = Router(name="premium")

# Простая "псевдо-БД" для примера. Замените на ваш репозиторий/БД.
_USER_PREMIUM_APPS: dict[int, str] = {}


class PremiumSG(StatesGroup):
    wait_goal = State()


# Вход в раздел
@router.message(Command("premium"))
@router.message(F.text == "⭐ Расширенная версия")
async def premium_entry(message: Message, state: FSMContext) -> None:
    uid = message.from_user.id
    has_app = uid in _USER_PREMIUM_APPS
    text = (
        "⭐ Расширенная версия\n\n"
        "• Ежедневный разбор и обратная связь\n"
        "• Разогрев голоса, дикции и внимания\n"
        "• Мини-кастинг и «путь лидера»\n\n"
        "Выберите действие:"
    )
    await state.clear()
    await message.answer(text, reply_markup=premium_kb(has_app))


# Что внутри
@router.message(F.text == "🔎 Что внутри")
async def premium_inside(message: Message) -> None:
    await message.answer(
        "Внутри расширенной версии — больше практики и персональных разборов.",
        reply_markup=premium_kb(has_application=(message.from_user.id in _USER_PREMIUM_APPS)),
    )


# Оставить заявку
@router.message(F.text == "📝 Оставить заявку")
async def premium_ask_goal(message: Message, state: FSMContext) -> None:
    await state.set_state(PremiumSG.wait_goal)
    await message.answer(
        "Напишите цель одной короткой фразой (до 200 символов). Если передумали — отправьте /cancel."
    )


@router.message(PremiumSG.wait_goal, F.text.len() <= 200)
async def premium_save_goal(message: Message, state: FSMContext) -> None:
    _USER_PREMIUM_APPS[message.from_user.id] = message.text.strip()
    await state.clear()
    await message.answer("Спасибо! Принял. Двигаемся дальше 👍", reply_markup=premium_kb(has_application=True))


@router.message(PremiumSG.wait_goal)
async def premium_goal_too_long(message: Message) -> None:
    await message.answer("Слишком длинно 🙈 Отправьте цель одной короткой фразой (до 200 символов) или /cancel.")


# Мои заявки
@router.message(F.text == "📂 Мои заявки")
async def premium_my_apps(message: Message) -> None:
    uid = message.from_user.id
    if uid not in _USER_PREMIUM_APPS:
        await message.answer("Заявок пока нет.", reply_markup=premium_kb(has_application=False))
        return
    goal = _USER_PREMIUM_APPS[uid]
    await message.answer(f"Ваша заявка:\n— {goal}", reply_markup=premium_kb(has_application=True))


# Единая навигация «В меню» — только reply-кнопка
@router.message(F.text == "📎 В меню")
async def premium_to_menu(message: Message) -> None:
    await message.answer("Ок, вернулись в главное меню. Нажми нужную кнопку снизу.", reply_markup=main_menu_kb())


# Страховка на /cancel из премиума
@router.message(Command("cancel"))
async def premium_cancel(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Ок, вернулись в главное меню.", reply_markup=main_menu_kb())
