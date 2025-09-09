# app/routers/menu.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

router = Router(name="menu")


# ---------- helpers ----------

def main_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🏋️‍♀️ Тренировка дня", callback_data="menu_training"),
            InlineKeyboardButton(text="📈 Мой прогресс",     callback_data="menu_progress"),
        ],
        [
            InlineKeyboardButton(text="🧭 Путь лидера (заявка)", callback_data="menu_apply"),
            InlineKeyboardButton(text="🤖 Наставник: спросить",  callback_data="menu_ask"),
        ],
        [
            InlineKeyboardButton(text="🔐 Политика / удалить данные", callback_data="menu_privacy"),
        ],
        [
            InlineKeyboardButton(text="❓ Справка", callback_data="menu_help"),
        ],
    ])


# ---------- commands ----------

@router.message(Command("menu"))
async def menu_cmd(m: Message):
    await m.answer("Выбери действие:", reply_markup=main_kb())


# ---------- callbacks ----------

@router.callback_query(F.data == "menu_training")
async def menu_training(cb: CallbackQuery):
    # Просто «переадресуем» пользователя на команду /training
    await cb.message.answer("/training")
    await cb.answer()

@router.callback_query(F.data == "menu_progress")
async def menu_progress(cb: CallbackQuery):
    await cb.message.answer("/progress")
    await cb.answer()

@router.callback_query(F.data == "menu_apply")
async def menu_apply(cb: CallbackQuery):
    await cb.message.answer("/apply")
    await cb.answer()

@router.callback_query(F.data == "menu_ask")
async def menu_ask(cb: CallbackQuery):
    # Подскажем, как спросить наставника
    await cb.message.answer("Напиши коротко свой запрос и запусти сессию наставника командой /coach_on\n"
                            "Пример: «/ask зажим в горле»")
    await cb.answer()


# ---------- privacy & wipe (ленивые импорты из system.py) ----------

@router.callback_query(F.data == "menu_privacy")
async def menu_privacy(cb: CallbackQuery):
    # ВАЖНО: импорт внутри хендлера → не будет круговой зависимости
    from app.routers.system import PRIVACY_TEXT
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🗑 Удалить профиль", callback_data="menu_wipe")],
        [InlineKeyboardButton(text="⬅️ Назад в меню",   callback_data="menu_back")],
    ])
    await cb.message.answer(PRIVACY_TEXT + "\n\nНапоминание: /wipe_me — полное удаление профиля.",
                            reply_markup=kb)
    await cb.answer()


@router.callback_query(F.data == "menu_wipe")
async def menu_wipe(cb: CallbackQuery, state: FSMContext):
    # Ленивые импорты из system.py
    from app.routers.system import WipeFlow, _wipe_kb
    await state.set_state(WipeFlow.confirm)
    await cb.message.answer(
        "⚠️ Вы собираетесь удалить профиль и все записи. Действие необратимо. Подтвердить?",
        reply_markup=_wipe_kb()
    )
    await cb.answer()


@router.callback_query(F.data == "menu_back")
async def menu_back(cb: CallbackQuery):
    await cb.message.answer("Ок, что дальше?", reply_markup=main_kb())
    await cb.answer()


# ---------- справка ----------

@router.callback_query(F.data == "menu_help")
async def menu_help(cb: CallbackQuery):
    text = (
        "Команды:\n"
        "/start — начать онбординг\n"
        "/menu — открыть меню\n"
        "/training — тренировка дня\n"
        "/progress — мой прогресс\n"
        "/apply — Путь лидера (заявка)\n"
        "/coach_on — включить наставника\n"
        "/coach_off — выключить наставника\n"
        "/ask <вопрос> — спросить наставника\n"
        "/privacy — политика и удаление данных\n"
        "/wipe_me — удалить профиль"
    )
    await cb.message.answer(text)
    await cb.answer()
