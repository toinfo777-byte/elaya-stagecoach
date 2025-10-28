from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup

router = Router(name="entrypoints")


def _menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Меню")],
            [KeyboardButton(text="/ping"), KeyboardButton(text="/hq"), KeyboardButton(text="/faq")],
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
    )


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    await message.answer(
        "Привет! Я — «Элайя — Тренер сцены». Готов к работе.\n"
        "Команды: /ping /hq /faq\n"
        "Нажми «Меню», чтобы открыть клавиатуру.",
        reply_markup=_menu_kb(),
    )


@router.message(F.text == "Меню")
async def show_menu(message: Message) -> None:
    await message.answer("Меню открыто. Используй кнопки или команды.", reply_markup=_menu_kb())


@router.message(Command("ping"))
async def cmd_ping(message: Message) -> None:
    await message.answer("pong 🟢")


@router.message(Command("hq"))
async def cmd_hq(message: Message) -> None:
    await message.answer(
        "🛰 HQ-сводка\n"
        "• ENV: web\n"
        "• MODE: webhook\n"
        "• Отчёт: проверьте daily/post-deploy отчёты (если подключены)"
    )


@router.message(Command("faq"))
async def cmd_faq(message: Message) -> None:
    await message.answer(
        "❓ FAQ\n"
        "• /start — перезапустить меню\n"
        "• /ping — быстрая проверка связи\n"
        "• /hq — краткая служебная сводка"
    )
