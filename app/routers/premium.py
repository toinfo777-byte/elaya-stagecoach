from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from app.keyboards.menu import BTN_PREMIUM
from app.storage.repo import session_scope
from app.storage.models import Feedback  # если нужно логировать интерес; можно убрать

router = Router(name="premium")

def kb_premium_menu() -> ReplyKeyboardMarkup:
    rows = [
        [KeyboardButton(text="Что внутри"), KeyboardButton(text="Оставить заявку")],
        [KeyboardButton(text="Мои заявки"), KeyboardButton(text="🫡 В меню")],
    ]
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True, is_persistent=True)

@router.message(Command("premium"))
@router.message(F.text == BTN_PREMIUM)
async def premium_entry(msg: Message) -> None:
    await msg.answer(
        "⭐️ Расширенная версия\n\n"
        "• Ежедневный разбор и обратная связь\n"
        "• Разогрев голоса, дикции и внимания\n"
        "• Мини-кастинг и путь лидера\n\n"
        "Выберите действие:", reply_markup=kb_premium_menu()
    )

@router.message(F.text == "Что внутри")
async def premium_inside(msg: Message) -> None:
    await msg.answer(
        "Внутри — тренировки, обратная связь, задания и материалы.\n"
        "Можно начать в любой день. Напишите заявку — свяжемся.", reply_markup=kb_premium_menu()
    )

@router.message(F.text == "Оставить заявку")
async def premium_leave_request(msg: Message) -> None:
    # Сохраним «заявку» как feedback с context='premium' (если нет таблицы — можно заменить на Event)
    with session_scope() as s:
        try:
            s.add(Feedback(
                user_id=None,  # если есть current_user.id — подставьте
                context="premium",
                text=f"request from tg:{msg.from_user.id} @{msg.from_user.username or '-'}",
            ))
            # session_scope сам коммитит
        except Exception:
            pass

    await msg.answer("Заявка принята ✅ (без записи в БД). Мы свяжемся или включим доступ автоматически.", reply_markup=kb_premium_menu())

@router.message(F.text == "Мои заявки")
async def premium_my_requests(msg: Message) -> None:
    # Демонстрационный вывод (без реальной выборки)
    await msg.answer("Мои заявки:\n• #1 — новая ●", reply_markup=kb_premium_menu())

@router.message(F.text == "🫡 В меню")
async def premium_back_to_menu(msg: Message) -> None:
    from app.keyboards.menu import main_menu
    await msg.answer("Ок, вернулись в главное меню. Нажми нужную кнопку снизу.", reply_markup=main_menu())
