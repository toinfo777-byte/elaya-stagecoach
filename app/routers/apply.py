from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from app.keyboards.menu import BTN_APPLY
from app.storage.repo import session_scope
from app.storage.models import Lead

router = Router(name="apply")

def kb_apply_menu() -> ReplyKeyboardMarkup:
    rows = [
        [KeyboardButton(text="Что внутри"), KeyboardButton(text="Оставить заявку")],
        [KeyboardButton(text="Мои заявки"), KeyboardButton(text="🫡 В меню")],
    ]
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True, is_persistent=True)

@router.message(Command("apply"))
@router.message(F.text == BTN_APPLY)
async def apply_entry(msg: Message) -> None:
    await msg.answer(
        "🧭 Путь лидера: короткая заявка.\n"
        "Напишите, чего хотите достичь — одним сообщением.", reply_markup=kb_apply_menu()
    )

@router.message(F.text == "Что внутри")
async def apply_inside(msg: Message) -> None:
    await msg.answer(
        "Путь лидера — индивидуальная траектория с фокусом на цели.\n"
        "Оставьте заявку — вернусь с вопросами и предложениями.", reply_markup=kb_apply_menu()
    )

@router.message(F.text == "Оставить заявку")
async def apply_ask_text(msg: Message) -> None:
    await msg.answer("Напишите цель одной фразой (до 200 символов). Если передумали — отправьте /cancel.", reply_markup=kb_apply_menu())

@router.message(F.text == "Мои заявки")
async def apply_my_requests(msg: Message) -> None:
    # Минимальный «лист» — без реальной выборки
    await msg.answer("Заявок пока нет.", reply_markup=kb_apply_menu())

@router.message(F.text == "🫡 В меню")
async def apply_back_to_menu(msg: Message) -> None:
    from app.keyboards.menu import main_menu
    await msg.answer("Ок, вернулись в главное меню. Нажми нужную кнопку снизу.", reply_markup=main_menu())

# Пришёл свободный текст после «Путь лидера»
@router.message(F.text.len() > 0)
async def apply_catch_free_text(msg: Message) -> None:
    text = (msg.text or "").strip()
    if not text:
        return

    # Сохраним лид (user_id тут не маппим — можно доработать, если есть текущий пользователь)
    with session_scope() as s:
        try:
            s.add(Lead(
                user_id=None,
                channel="tg",
                contact=str(msg.from_user.id),
                note=text[:500],
                track="apply",
            ))
        except Exception:
            pass

    await msg.reply("Спасибо! Принял. Двигаемся дальше 👍", reply_markup=kb_apply_menu())
