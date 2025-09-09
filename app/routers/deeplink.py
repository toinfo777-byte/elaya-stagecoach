from __future__ import annotations

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.filters.command import CommandObject
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

# будем вызывать готовые входы из других роутеров
from app.routers.casting import casting_entry            # мини-кастинг
from app.routers.coach import coach_on                   # включить наставника

router = Router(name="deeplink")


@router.message(CommandStart())
async def start_plain(m: Message):
    # обычный /start без payload — пусть идёт дальше по твоему онбордингу/меню
    await m.answer("Привет! Открой меню или используй команды: /training /casting /coach_on.")


@router.message(CommandStart(deep_link=True))
async def start_deeplink(m: Message, command: CommandObject, state: FSMContext):
    payload = (command.args or "").strip().lower()

    if payload in {"go_casting", "casting"}:
        # сразу запускаем мини-кастинг
        return await casting_entry(m, state)

    if payload in {"coach", "go_coach", "mentor"}:
        # включаем сессию наставника на N минут
        return await coach_on(m)

    if payload in {"go_training", "training"}:
        # если нет явного входа в training, даём понятный шаг
        return await m.answer("Открываю тренировку дня. Нажми /training")

    # неизвестный payload — мягко объясняем
    await m.answer("Не распознал ссылку. Открой меню: /menu")
