# app/routers/premium.py
from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router(name="premium")

TITLE = "⭐️ Расширенная версия"
BODY = (
    "• Ежедневный разбор и обратная связь\n"
    "• Разогрев голоса, дикции и внимания\n"
    "• Мини-кастинг и «путь лидера»"
)

BTN_WHATS_INSIDE = "🔎 Что внутри"
BTN_APPLY = "📝 Оставить заявку"
BTN_MY_APPLIES = "📄 Мои заявки"
BTN_TO_MENU = "📣 В меню"

INSIDE_TEXT = "Внутри расширенной версии — больше практики и персональных разборов."
EMPTY_LIST = "Заявок пока нет."

ASK_TEXT = (
    "Напишите цель одной короткой фразой (до 200 символов). Если передумали — отправьте /cancel."
)
CONFIRM_TEXT = "Спасибо! Принял. Двигаемся дальше 👍"

TRIGGERS = {
    "расширенная версия",
    "⭐️ расширенная версия",
}

def _menu_text() -> str:
    return f"<b>{TITLE}</b>\n\n{BODY}\n\nВыберите действие:"

# Открытие раздела
@router.message(Command("premium"))
async def premium_cmd(message: Message) -> None:
    await message.answer(_menu_text())

@router.message(F.text.casefold().in_(t.lower() for t in TRIGGERS))
async def premium_text(message: Message) -> None:
    await message.answer(_menu_text())

# Что внутри
@router.message(F.text == BTN_WHATS_INSIDE)
async def premium_inside(message: Message) -> None:
    await message.answer(INSIDE_TEXT)

# Мои заявки (простой заглушечный список)
@router.message(F.text == BTN_MY_APPLIES)
async def premium_my_applies(message: Message) -> None:
    # TODO: подставьте реальные заявки из БД
    await message.answer(EMPTY_LIST)

# Оставить заявку — спрашиваем текст цели
@router.message(F.text == BTN_APPLY)
async def premium_apply_ask(message: Message) -> None:
    await message.answer(ASK_TEXT)

# Сохранение заявки: любое «обычное» текстовое сообщение,
# которое не является служебной командой/кнопкой и не длиннее 200 символов
@router.message(F.text & ~Command())
async def premium_apply_save(message: Message) -> None:
    t = (message.text or "").strip()
    if not t:
        return
    # Не ловим системные/менюшные сообщения, чтобы «спасибо» не сыпалось лишний раз
    skip = {
        BTN_WHATS_INSIDE, BTN_APPLY, BTN_MY_APPLIES, BTN_TO_MENU,
        "Меню", "Меню", "/menu", "/start", "/training", "/progress", "/casting", "/apply", "/settings", "/premium"
    }
    if t in skip:
        return
    if len(t) > 200:
        await message.answer("Слишком длинно. Сформулируйте цель до 200 символов.")
        return

    # TODO: сохранить заявку в БД (user_id, text)
    # repo.save_premium_apply(user_id=message.from_user.id, goal=t)

    # Подтверждаем и НЕ предлагаем «Оставить заявку» снова
    await message.answer(CONFIRM_TEXT)
    # Возвращение в главное меню — у вас уже есть нижняя кнопка «📣 В меню»
