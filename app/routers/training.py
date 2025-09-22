# app/routers/training.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from app.keyboards.menu import main_menu, BTN_TRAINING
from app.keyboards.training import levels_kb, actions_kb, skip_confirm_kb
from app.storage.repo import log_training  # <-- новый контракт

router = Router(name="training")

TRAINING_PROGRAMS = {
    "beginner": "Разогрев · 5 минут\n1) Дыхание: 1 мин\n2) Рот–язык–щелчки: 2 мин\n3) Артикуляция: 2 мин\n💡 Совет: запиши 15 сек до/после.",
    "medium":   "Голос · 10 минут\n1) Гудение на «м»: 2 мин\n2) Скольжения («сирена»): 3 мин\n3) Чистая дикция: 5 скороговорок\n💡 Совет: говори медленнее обычного.",
    "pro":      "Сцена · 15 минут\n1) Дых. цикл: 3 мин\n2) Резонаторы: 5 мин\n3) Текст с задачей: 7 мин\n💡 Совет: работай стоя, корпус свободен.",
}

async def show_training_levels(message: Message):
    """Показать экран выбора уровня (можно вызывать из диплинка)."""
    await message.answer(
        "Тренировка дня\n\nВыбери уровень. После выполнения нажми «Выполнил(а)».",
        reply_markup=levels_kb(),
    )

@router.message(F.text == BTN_TRAINING)  # кнопка в меню
async def training_entry(m: Message):
    await show_training_levels(m)

@router.callback_query(F.data.startswith("training:level:"))
async def on_level_pick(c: CallbackQuery, state: FSMContext):
    level = c.data.split(":")[-1]
    await state.update_data(level=level)
    await c.message.answer(TRAINING_PROGRAMS[level], reply_markup=actions_kb(level))
    await c.answer()  # гасим «спиннер»

@router.callback_query(F.data.startswith("training:done:"))
async def on_done(c: CallbackQuery, state: FSMContext):
    # сначала погасим «спиннер» чтобы inline-кнопка не висела
    await c.answer("Засчитано!")
    # уровень берём из callback-data, а если что — из state
    level = c.data.split(":")[-1] if ":" in c.data else (await state.get_data()).get("level", "beginner")
    # запись в БД (дату берёт сам репозиторий)
    await log_training(c.from_user.id, level=level, done=True)
    await c.message.answer("🔥 Отлично! День засчитан. Увидимся завтра!", reply_markup=main_menu())

@router.callback_query(F.data.startswith("training:skip:"))
async def on_skip_request(c: CallbackQuery, state: FSMContext):
    level = c.data.split(":")[-1]
    await state.update_data(level=level)
    await c.message.answer("Пропустить тренировку сегодня?", reply_markup=skip_confirm_kb(level))
    await c.answer()

@router.callback_query(F.data.startswith("training:skip-confirm:"))
async def on_skip_confirm(c: CallbackQuery, state: FSMContext):
    await c.answer("Пропущено")
    level = c.data.split(":")[-1] if ":" in c.data else (await state.get_data()).get("level", "beginner")
    await log_training(c.from_user.id, level=level, done=False)
    await c.message.answer("Ок, вернёмся завтра.", reply_markup=main_menu())

@router.callback_query(F.data.startswith("training:skip-cancel:"))
async def on_skip_cancel(c: CallbackQuery):
    await c.message.answer("Тогда выбирай уровень ещё раз 👇", reply_markup=levels_kb())
    await c.answer("Отменено")

# ── Сверхприоритетный выход в меню ────────────────────────────────
@router.message(F.text.in_({"Меню", "/menu"}))
async def leave_to_menu(m: Message, state: FSMContext):
    await state.clear()
    await m.answer("Готово! Открываю меню.", reply_markup=main_menu())
