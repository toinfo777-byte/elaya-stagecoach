# app/routers/premium.py
from __future__ import annotations

from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
)

from app.keyboards.menu import (
    BTN_PREMIUM,
    main_menu,
)

router = Router(name="premium")

# ---------- Вспомогательная клавиатура премиум-блока ----------
def premium_kb() -> ReplyKeyboardMarkup:
    rows = [
        [KeyboardButton(text="Что внутри")],
        [KeyboardButton(text="Оставить заявку")],
        [KeyboardButton(text="Мои заявки")],
        [KeyboardButton(text="📣 В меню")],
    ]
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True, is_persistent=True)


# ---------- Тексты ----------
PREMIUM_INTRO = (
    "⭐️ <b>Расширенная версия</b>\n\n"
    "• Ежедневный разбор и обратная связь\n"
    "• Разогрев голоса, дикции и внимания\n"
    "• Мини-кастинг и путь лидера\n\n"
    "Выберите действие:"
)

PREMIUM_WHATS_INSIDE = (
    "Внутри — тренировки, обратная связь и прогресс. "
    "Запросы на подключение принимаем через «Оставить заявку»."
)


# ===================== ОБРАБОТЧИКИ =====================

async def _open_premium(message: types.Message) -> None:
    """Показать входное меню премиума."""
    await message.answer(PREMIUM_INTRO, reply_markup=premium_kb())


# 1) Открыть премиум: команда /premium
@router.message(Command("premium"))
async def premium_cmd(message: types.Message) -> None:
    await _open_premium(message)


# 2) Открыть премиум: клик по кнопке в главном меню (или где угодно)
@router.message(F.text == BTN_PREMIUM)
async def premium_btn(message: types.Message) -> None:
    await _open_premium(message)


# 3) Что внутри
@router.message(F.text == "Что внутри")
async def premium_inside(message: types.Message) -> None:
    await message.answer(PREMIUM_WHATS_INSIDE, reply_markup=premium_kb())


# 4) Оставить заявку — здесь пока только заглушка (логика заявки у вас в apply/lead)
@router.message(F.text == "Оставить заявку")
async def premium_apply(message: types.Message) -> None:
    await message.answer(
        "Напишите цель одной фразой (до 200 символов). Если передумали — отправьте /cancel.",
        reply_markup=premium_kb(),
    )
    # если нужно сразу переключать в FSM «Путь лидера», можно тут вызывать ваш хендлер из routers.apply


# 5) Мои заявки — заглушка/список (если логика уже есть в другом роутере, можно редиректнуть туда)
@router.message(F.text == "Мои заявки")
async def premium_my_requests(message: types.Message) -> None:
    await message.answer("Заявок пока нет.", reply_markup=premium_kb())


# 6) Вернуться в главное меню
@router.message(F.text == "📣 В меню")
async def premium_back_to_menu(message: types.Message) -> None:
    await message.answer("Ок, вернулись в главное меню. Нажми нужную кнопку снизу.", reply_markup=main_menu())
