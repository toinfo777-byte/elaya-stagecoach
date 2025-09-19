from __future__ import annotations

from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.utils.markdown import hbold as b

from app.keyboards.menu import (
    BTN_PREMIUM,
    main_menu,
)
from app.storage.repo import session_scope, add_premium_request_for_tg, list_premium_requests_for_tg

router = Router(name="premium")


# ── Клавиатуры ────────────────────────────────────────────────────────────────
def kb_premium_menu() -> types.ReplyKeyboardMarkup:
    rows = [
        [types.KeyboardButton(text="Что внутри")],
        [types.KeyboardButton(text="Оставить заявку")],
        [types.KeyboardButton(text="Мои заявки")],
        [types.KeyboardButton(text="📣 В меню")],
    ]
    return types.ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True, is_persistent=True)


# ── Вход в раздел ─────────────────────────────────────────────────────────────
@router.message(F.text == BTN_PREMIUM)
@router.message(Command("premium"))
async def premium_entry(msg: types.Message) -> None:
    await msg.answer(
        f"{b('⭐️ Расширенная версия')}\n\n"
        "• Ежедневный разбор и обратная связь\n"
        "• Разогрев голоса, дикции и внимания\n"
        "• Мини-кастинг и путь лидера\n\n"
        f"{b('Выберите действие:')}",
        reply_markup=kb_premium_menu(),
    )


# ── Что внутри ────────────────────────────────────────────────────────────────
@router.message(F.text == "Что внутри")
async def premium_what(msg: types.Message) -> None:
    await msg.answer(
        "Внутри — индивидуальные задания, регулярный разбор и персональная обратная связь. "
        "Можно начать со свободной заявки: коротко опишите цель.",
        reply_markup=kb_premium_menu(),
    )


# ── Оставить заявку ───────────────────────────────────────────────────────────
@router.message(F.text == "Оставить заявку")
async def premium_request_start(msg: types.Message) -> None:
    await msg.answer(
        f"{b('Путь лидера: короткая заявка.')} \n"
        "Напишите, чего хотите достичь — одним сообщением (до 200 символов).\n"
        "Если передумали — отправьте /cancel.",
        reply_markup=kb_premium_menu(),
    )


@router.message(F.text, F.text.len() > 0, F.text != "Что внутри", F.text != "Мои заявки", F.text != "📣 В меню")
async def premium_request_catch_text(msg: types.Message) -> None:
    """
    Если юзер находится в разделе «Расширенная версия» и написал произвольный
    текст после «Оставить заявку», просто сохраняем как заявку.
    (Формальный FSM не делаем, чтобы не зависать на шагах.)
    """
    # Чтобы не перехватывать всё подряд, проверим, что последнее меню было премиум:
    # простая эвристика: ниже клавиатура премиума всегда активна — позволяем сохранять.
    text = (msg.text or "").strip()
    if not text or text.startswith("/"):
        return

    with session_scope() as s:
        add_premium_request_for_tg(
            s,
            tg_id=msg.from_user.id,
            username=msg.from_user.username,
            text_note=text,
            source="premium_text",
        )

    await msg.answer("Спасибо! Заявка принята ✅", reply_markup=kb_premium_menu())


# ── Мои заявки ────────────────────────────────────────────────────────────────
@router.message(F.text == "Мои заявки")
async def premium_my_requests(msg: types.Message) -> None:
    with session_scope() as s:
        items = list_premium_requests_for_tg(s, msg.from_user.id)

    if not items:
        await msg.answer("Заявок пока нет.", reply_markup=kb_premium_menu())
        return

    lines = [f"{b('Мои заявки')}: #{len(items)}"]
    for idx, it in enumerate(items, 1):
        note = (it.meta or {}).get("note") or "—"
        lines.append(f"{idx}. {it.created_at:%d.%m %H:%M} — {it.status} — {note[:100]}")
    await msg.answer("\n".join(lines), reply_markup=kb_premium_menu())


# ── В меню ────────────────────────────────────────────────────────────────────
@router.message(F.text == "📣 В меню")
async def premium_back_to_menu(msg: types.Message) -> None:
    await msg.answer("Ок, вернулись в главное меню. Нажми нужную кнопку снизу.", reply_markup=main_menu())
