# app/routers/training.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from app.keyboards.menu import main_menu, BTN_TRAINING
from app.keyboards.training import levels_kb, actions_kb, skip_confirm_kb
from app.storage.repo import log_training  # новый контракт

router = Router(name="training")

TRAINING_PROGRAMS = {
    "beginner": "Разогрев · 5 минут\n1) Дыхание: 1 мин\n2) Рот–язык–щелчки: 2 мин\n3) Артикуляция: 2 мин\n💡 Совет: запиши 15 сек до/после.",
    "medium":   "Голос · 10 минут\n1) Гудение на «м»: 2 мин\n2) Скольжения («сирена»): 3 мин\n3) Чистая дикция: 5 скороговорок\n💡 Совет: говори медленнее обычного.",
    "pro":      "Сцена · 15 минут\n1) Дых. цикл: 3 мин\n2) Резонаторы: 5 мин\n3) Текст с задачей: 7 мин\n💡 Совет: работай стоя, корпус свободен.",
}

# ── утилита: аккуратно достаём уровень из разных схем callback_data ──
def _extract_level(data: str, default: str = "beginner") -> str:
    """
    Поддерживаем форматы:
      training:level:<lvl>
      training:done:<lvl>
      training:skip:<lvl>
      training:skip-confirm:<lvl>
      training:skip-cancel:<lvl>
      tr:lvl:<lvl>     (старый)
      tr:done:<lvl>    (старый)
      tr:skip:<lvl>    (старый)
    """
    try:
        parts = data.split(":")
        # последние 1–2 токена могут содержать уровень
        for tok in reversed(parts):
            if tok in ("beginner", "medium", "pro"):
                return tok
    except Exception:
        pass
    return default


# ── публичная точка (для диплинка) ─────────────────────────────────
async def show_training_levels(message: Message):
    """Показать экран выбора уровня (используется и из диплинков)."""
    await message.answer(
        "Тренировка дня\n\nВыбери уровень. После выполнения нажми «Выполнил(а)».",
        reply_markup=levels_kb(),
    )

# алиас, если где-то зовётся именно start_training
start_training = show_training_levels


# ── вход с кнопки меню ─────────────────────────────────────────────
@router.message(F.text == BTN_TRAINING)
async def training_entry(m: Message):
    await show_training_levels(m)


# ── выбор уровня ───────────────────────────────────────────────────
@router.callback_query(F.data.startswith("training:level:"))
async def on_level_pick(c: CallbackQuery, state: FSMContext):
    await c.answer()
    level = _extract_level(c.data)
    await state.update_data(level=level)
    await c.message.answer(TRAINING_PROGRAMS[level], reply_markup=actions_kb(level))

# совместимость со старым форматом: tr:lvl:<lvl>
@router.callback_query(F.data.startswith("tr:lvl:"))
async def on_level_pick_legacy(c: CallbackQuery, state: FSMContext):
    await c.answer()
    level = _extract_level(c.data)
    await state.update_data(level=level)
    await c.message.answer(TRAINING_PROGRAMS[level], reply_markup=actions_kb(level))


# ── выполнено ──────────────────────────────────────────────────────
@router.callback_query(F.data.startswith("training:done:"))
async def on_done_with_lvl(c: CallbackQuery, state: FSMContext):
    await c.answer("Засчитано!")
    level = _extract_level(c.data) or (await state.get_data()).get("level", "beginner")
    await log_training(c.from_user.id, level=level, done=True)
    await c.message.answer("🔥 Отлично! День засчитан. Увидимся завтра!", reply_markup=main_menu())

# поддержка кнопки без уровня: callback_data="training:done"
@router.callback_query(F.data == "training:done")
async def on_done_plain(c: CallbackQuery, state: FSMContext):
    await c.answer("Засчитано!")
    level = (await state.get_data()).get("level", "beginner")
    await log_training(c.from_user.id, level=level, done=True)
    await c.message.answer("🔥 Отлично! День засчитан. Увидимся завтра!", reply_markup=main_menu())

# совместимость со старым форматом: tr:done:<lvl>
@router.callback_query(F.data.startswith("tr:done:"))
async def on_done_legacy(c: CallbackQuery, state: FSMContext):
    await c.answer("Засчитано!")
    level = _extract_level(c.data) or (await state.get_data()).get("level", "beginner")
    await log_training(c.from_user.id, level=level, done=True)
    await c.message.answer("🔥 Отлично! День засчитан. Увидимся завтра!", reply_markup=main_menu())


# ── запрос на пропуск ──────────────────────────────────────────────
@router.callback_query(F.data.startswith("training:skip:"))
async def on_skip_request(c: CallbackQuery, state: FSMContext):
    await c.answer()
    level = _extract_level(c.data) or (await state.get_data()).get("level", "beginner")
    await state.update_data(level=level)
    await c.message.answer("Пропустить тренировку сегодня?", reply_markup=skip_confirm_kb(level))

# кнопка без уровня: callback_data="training:skip"
@router.callback_query(F.data == "training:skip")
async def on_skip_request_plain(c: CallbackQuery, state: FSMContext):
    await c.answer()
    level = (await state.get_data()).get("level", "beginner")
    await c.message.answer("Пропустить тренировку сегодня?", reply_markup=skip_confirm_kb(level))

# совместимость: tr:skip:<lvl>
@router.callback_query(F.data.startswith("tr:skip:"))
async def on_skip_request_legacy(c: CallbackQuery, state: FSMContext):
    await c.answer()
    level = _extract_level(c.data) or (await state.get_data()).get("level", "beginner")
    await state.update_data(level=level)
    await c.message.answer("Пропустить тренировку сегодня?", reply_markup=skip_confirm_kb(level))


# ── подтверждение пропуска ─────────────────────────────────────────
@router.callback_query(F.data.startswith("training:skip-confirm:"))
async def on_skip_confirm(c: CallbackQuery, state: FSMContext):
    await c.answer("Пропущено")
    level = _extract_level(c.data) or (await state.get_data()).get("level", "beginner")
    await log_training(c.from_user.id, level=level, done=False)
    await c.message.answer("Ок, вернёмся завтра.", reply_markup=main_menu())

@router.callback_query(F.data == "training:skip-confirm")
async def on_skip_confirm_plain(c: CallbackQuery, state: FSMContext):
    await c.answer("Пропущено")
    level = (await state.get_data()).get("level", "beginner")
    await log_training(c.from_user.id, level=level, done=False)
    await c.message.answer("Ок, вернёмся завтра.", reply_markup=main_menu())


# ── отмена пропуска ────────────────────────────────────────────────
@router.callback_query(F.data.startswith("training:skip-cancel:"))
async def on_skip_cancel(c: CallbackQuery):
    await c.answer("Отменено")
    await c.message.answer("Тогда выбирай уровень ещё раз 👇", reply_markup=levels_kb())

@router.callback_query(F.data == "training:skip-cancel")
async def on_skip_cancel_plain(c: CallbackQuery):
    await c.answer("Отменено")
    await c.message.answer("Тогда выбирай уровень ещё раз 👇", reply_markup=levels_kb())


# ── сверхприоритетный выход в меню ─────────────────────────────────
@router.message(F.text.in_({"Меню", "/menu"}))
async def leave_to_menu(m: Message, state: FSMContext):
    await state.clear()
    await m.answer("Готово! Открываю меню.", reply_markup=main_menu())
