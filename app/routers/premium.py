from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from app.keyboards.menu import (
    BTN_PREMIUM,  # "⭐️ Расширенная версия"
)
from app.keyboards.menu import main_menu  # наше нижнее меню
from app.storage.repo import session_scope, log_event
from app.storage.models import User, Lead
from app.config import settings

router = Router(name="premium")

# --- локальная клавиатура блока ---
def kb_premium() -> ReplyKeyboardMarkup:
    rows = [
        [KeyboardButton(text="Что внутри"), KeyboardButton(text="Оставить заявку")],
        [KeyboardButton(text="Мои заявки"), KeyboardButton(text="📣 В меню")],
    ]
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True, is_persistent=True)


class PremiumSG(StatesGroup):
    waiting_request_text = State()


TEXT_WHATS_INSIDE = (
    "⭐️ <b>Расширенная версия</b>\n\n"
    "• Ежедневный мини-разбор и обратная связь\n"
    "• Разогрев голоса, дикция и внимание\n"
    "• Мини-кастинг и «путь лидера»\n\n"
    "Нажми «Оставить заявку» — это коротко. Я свяжусь с тобой в чате."
)


def _admin_chat_id() -> int | None:
    try:
        v = getattr(settings, "ADMIN_ALERT_CHAT_ID", None)
        if not v:
            return None
        return int(str(v).strip())
    except Exception:
        return None


async def _send_admin_alert(text: str) -> None:
    """
    Пассивное оповещение админа (не критично, если не вышло).
    Используем dp.bot через контекст нельзя: импорт в точке вызова.
    """
    admin = _admin_chat_id()
    if not admin:
        return
    try:
        from aiogram import Bot
        from app.main import _resolve_token  # тот же хелпер, что в main.py
        bot = Bot(token=_resolve_token())
        await bot.send_message(chat_id=admin, text=text)
    except Exception:
        pass


# --- вход в раздел ---
@router.message(Command("premium"))
@router.message(F.text == BTN_PREMIUM)
async def premium_entry(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("⭐️ Расширенная версия", reply_markup=kb_premium())


# --- что внутри ---
@router.message(F.text.lower().in_({"что внутри", "что внутри?"}))
async def premium_whats_inside(message: Message) -> None:
    await message.answer(TEXT_WHATS_INSIDE)


# --- в меню ---
@router.message(F.text.in_({"📣 В меню", "В меню"}))
async def premium_back_to_menu(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Ок, вернулись в главное меню. Нажми нужную кнопку снизу.", reply_markup=main_menu())


# --- оставить заявку: шаг 1 (вопрос) ---
@router.message(F.text.lower().in_({"оставить заявку"}))
async def premium_leave_request_ask(message: Message, state: FSMContext) -> None:
    await state.set_state(PremiumSG.waiting_request_text)
    await message.answer(
        "Напишите цель одной короткой фразой (до 200 символов).\n"
        "Если передумали — отправьте /cancel.",
    )


# --- оставить заявку: шаг 2 (сохранение) ---
@router.message(PremiumSG.waiting_request_text, F.text.len() > 0)
async def premium_leave_request_save(message: Message, state: FSMContext) -> None:
    text = (message.text or "").strip()
    if not text:
        await message.answer("Пустое сообщение. Напишите коротко, чего хотите достичь.")
        return
    if len(text) > 200:
        await message.answer("Слишком длинно 🙈 Сократите до 200 символов, пожалуйста.")
        return

    with session_scope() as s:
        # найдём/создадим пользователя
        u = s.query(User).filter_by(tg_id=message.from_user.id).first()
        if not u:
            u = User(tg_id=message.from_user.id, username=message.from_user.username or None, name=message.from_user.full_name)
            s.add(u)
            s.commit()

        lead = Lead(
            user_id=u.id,
            channel="tg",
            contact=f"@{u.username}" if u.username else str(u.tg_id),
            note=text,
            track="premium",
        )
        s.add(lead)
        s.commit()

        await _send_admin_alert(
            f"🆕 Заявка на ⭐️ Премиум от @{u.username or u.tg_id}\n"
            f"Цель: {text}"
        )
        log_event(s, u.id, "premium_request", {"text": text})

    await state.clear()
    await message.answer("Заявка принята ✅ Мы свяжемся с тобой или включим доступ автоматически.", reply_markup=kb_premium())


# --- список заявок текущего пользователя ---
@router.message(F.text.lower().in_({"мои заявки"}))
async def premium_my_requests(message: Message) -> None:
    with session_scope() as s:
        u = s.query(User).filter_by(tg_id=message.from_user.id).first()
        if not u:
            await message.answer("Заявок пока нет.")
            return
        q = (
            s.query(Lead)
            .filter(Lead.user_id == u.id, Lead.track == "premium")
            .order_by(Lead.ts.desc())
            .limit(5)
        )
        items = list(q)
        if not items:
            await message.answer("Заявок пока нет.")
            return

        lines = ["Мои заявки:"]
        for i, l in enumerate(items, 1):
            # простая метка статуса: пока «новая»
            lines.append(f"• #{i} — {l.ts:%d.%m %H:%M} — 🟡 новая\n  «{l.note}»")
        await message.answer("\n".join(lines), reply_markup=kb_premium())
