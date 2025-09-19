from __future__ import annotations

from aiogram import Router, F, types
from aiogram.filters import Command

from app.keyboards.menu import BTN_APPLY, main_menu
from app.storage.repo import session_scope, add_premium_request_for_tg

router = Router(name="apply")


def kb_apply_menu() -> types.ReplyKeyboardMarkup:
    rows = [
        [types.KeyboardButton(text="Оставить заявку")],
        [types.KeyboardButton(text="📣 В меню")],
    ]
    return types.ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True, is_persistent=True)


@router.message(F.text == BTN_APPLY)
@router.message(Command("apply"))
async def apply_entry(msg: types.Message) -> None:
    await msg.answer(
        "Путь лидера — индивидуальная траектория с фокусом на цели.\n"
        "Оставьте заявку — вернусь с вопросами и предложениями.",
        reply_markup=kb_apply_menu(),
    )


@router.message(F.text == "Оставить заявку")
async def apply_ask(msg: types.Message) -> None:
    await msg.answer(
        "Напишите цель одной короткой фразой (до 200 символов). Если передумали — отправьте /cancel.",
        reply_markup=kb_apply_menu(),
    )


@router.message(F.text, F.text.len() > 0, F.text != "📣 В меню")
async def apply_catch_text(msg: types.Message) -> None:
    text = (msg.text or "").strip()
    if not text or text.startswith("/"):
        return

    # Сохраняем как premium-заявку, чтобы она отображалась в «Мои заявки»
    with session_scope() as s:
        add_premium_request_for_tg(
            s,
            tg_id=msg.from_user.id,
            username=msg.from_user.username,
            text_note=text,
            source="apply",
        )

    await msg.answer("Спасибо! Принял. Двигаемся дальше 👍", reply_markup=main_menu())


@router.message(F.text == "📣 В меню")
async def apply_back(msg: types.Message) -> None:
    await msg.answer("Готово. Вот меню:", reply_markup=main_menu())
