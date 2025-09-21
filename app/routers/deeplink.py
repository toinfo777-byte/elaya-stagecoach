from __future__ import annotations

from aiogram import Router
from aiogram.filters import CommandStart, StateFilter
from aiogram.types import Message
from aiogram.filters.command import CommandObject
from aiogram.fsm.context import FSMContext

from app.keyboards.menu import main_menu
from app.storage.repo import session_scope
from app.storage.models import User

router = Router(name="deeplink")


def _has_profile(user_id: int) -> bool:
    with session_scope() as s:
        return s.query(User).filter(User.id == user_id).first() is not None


@router.message(StateFilter(None), CommandStart(deep_link=True))
async def start_with_payload(msg: Message, state: FSMContext, command: CommandObject):
    """
    Старт по ссылке:
      - если профиль уже есть — роутим сразу в нужный раздел
      - если профиля нет — сохраняем payload и передаём управление онбордингу (его /start)
    """
    payload = (command.args or "").strip() if command else ""

    if _has_profile(msg.from_user.id):
        # Пользователь есть — быстрое ветвление
        if payload.startswith("go_training"):
            await msg.answer("Запускаю тренировку дня…", reply_markup=main_menu())
            await msg.bot.send_message(msg.chat.id, "Тренировка дня")
            return
        if payload.startswith("go_casting"):
            await msg.answer("Открою мини-кастинг…", reply_markup=main_menu())
            await msg.bot.send_message(msg.chat.id, "Мини-кастинг")
            return

        # Непонятный payload — просто открываем меню
        await msg.answer("Готово. Вот меню:", reply_markup=main_menu())
        return

    # Профиля нет — положим payload в FSM и вызовем онбординг (/start)
    if payload:
        await state.update_data(start_payload=payload)

    # ПРОКСИ: вызываем онбординг-старт повторно (в том же апдейте это ок)
    # Aiogram доставит управление в onboarding.start
    await msg.answer("Давайте начнём с короткой анкеты, а потом перейдём по ссылке.")
    # Ничего больше не делаем: onboarding CommandStart(StateFilter(None)) перехватит следующий /start
