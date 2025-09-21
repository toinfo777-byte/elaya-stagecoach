from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from app.keyboards.menu import main_menu, BTN_TRAINING
from app.storage.mvp_repo import log_training

router = Router(name="training")

# Контент MVP (можно потом вынести в YAML)
LEVELS = {
    "beginner": {
        "title": "Разогрев · 5 минут",
        "content": (
            "1) Дыхание: 1 мин\n"
            "2) Рот–язык–щёлчки: 2 мин\n"
            "3) Артикуляция: 2 мин\n"
            "⚑ Совет: запиши 15 секунд речи до/после."
        )
    },
    "medium": {
        "title": "Голос · 10 минут",
        "content": (
            "1) Гудение на «м»: 2 мин\n"
            "2) Скольжения («сирена»): 3 мин\n"
            "3) Чистая дикция: 5 скороговорок\n"
            "⚑ Совет: говори чуть медленнее, чем обычно."
        )
    },
    "pro": {
        "title": "Сцена · 15 минут",
        "content": (
            "1) Дыхание + корпус: 3 мин\n"
            "2) Резонаторы: 5 мин\n"
            "3) Текст с задачей: 7 мин\n"
            "⚑ Совет: цель фразы > громкость."
        )
    },
}

def levels_kb() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text="🟢 Новичок", callback_data="lvl:beginner")],
        [InlineKeyboardButton(text="🟡 Средний", callback_data="lvl:medium")],
        [InlineKeyboardButton(text="🔴 Про", callback_data="lvl:pro")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)

def done_kb() -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(text="✅ Выполнил(а)", callback_data="train:done"),
            InlineKeyboardButton(text="⏭ Пропустить",  callback_data="train:skip"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


class TrainSG(StatesGroup):
    choose = State()
    running = State()


@router.message(F.text == BTN_TRAINING)
@router.message(Command("training"))
async def training_entry(m: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(TrainSG.choose)
    await m.answer(
        "Тренировка дня\n\n"
        "Выбери уровень. После выполнения нажми «Выполнил(а)».",
        reply_markup=main_menu()
    )
    await m.answer("Уровни:", reply_markup=levels_kb())


@router.callback_query(F.data.startswith("lvl:"), TrainSG.choose)
async def pick_level(cq: CallbackQuery, state: FSMContext) -> None:
    level = cq.data.split(":", 1)[1]
    data = LEVELS.get(level)
    if not data:
        await cq.answer("Неизвестный уровень", show_alert=True)
        return
    await state.update_data(level=level)
    await state.set_state(TrainSG.running)
    await cq.message.answer(
        f"<b>{data['title']}</b>\n{data['content']}",
        reply_markup=done_kb()
    )
    await cq.answer()


@router.callback_query(F.data == "train:done", TrainSG.running)
async def mark_done(cq: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    level = data.get("level", "beginner")
    log_training(cq.from_user.id, level, True)
    await state.clear()
    await cq.message.answer(
        "🔥 Отлично! День засчитан.\n"
        "Продолжай каждый день — «Тренировка дня» в один клик.",
        reply_markup=main_menu()
    )
    await cq.answer("Засчитано!")


@router.callback_query(F.data == "train:skip", TrainSG.running)
async def mark_skip(cq: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    level = data.get("level", "beginner")
    # Можно не логировать пропуск; оставим как «не выполнено»
    log_training(cq.from_user.id, level, False)
    await state.clear()
    await cq.message.answer("Ок, вернёмся завтра. 💫", reply_markup=main_menu())
    await cq.answer()
