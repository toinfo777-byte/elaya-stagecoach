from aiogram import Router, F
from aiogram.filters import Command  # ← уже добавлено
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from app.keyboards.menu import main_menu
from app.keyboards.feedback import feedback_kb            # <-- НОВОЕ
from app.storage.repo import session_scope
from app.storage.models import User, DrillRun
from app.services.drills import ensure_drills_in_db, choose_drill_for_user

router = Router(name="training")


class TrainingFlow(StatesGroup):
    steps = State()
    reflect_selecting = State()


def _step_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Далее ▶️", callback_data="step_next")],
            [
                InlineKeyboardButton(text="Пропустить ⏭️", callback_data="step_skip"),
                InlineKeyboardButton(text="Готово ✅", callback_data="step_done"),
            ],
        ]
    )


def _reflect_keyboard(selected: set[str], options: list[str]) -> InlineKeyboardMarkup:
    rows = []
    row = []
    for i, opt in enumerate(options):
        mark = "✅ " if opt in selected else ""
        row.append(InlineKeyboardButton(text=f"{mark}{opt}", callback_data=f"mk_{i}"))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton(text="Сохранить 💾", callback_data="mk_save")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ---------- Хелпер безопасного редактирования ----------
async def _safe_edit_text(msg, text: str, reply_markup: InlineKeyboardMarkup | None = None):
    """Редактируем текст, а если он не меняется — обновляем только клавиатуру."""
    try:
        await msg.edit_text(text, reply_markup=reply_markup)
    except TelegramBadRequest as e:
        if "message is not modified" in str(e).lower():
            if reply_markup:
                try:
                    await msg.edit_reply_markup(reply_markup=reply_markup)
                except TelegramBadRequest:
                    pass
        else:
            raise
# -------------------------------------------------------


@router.message(F.text == "🎯 Тренировка дня")
async def training_entry(m: Message, state: FSMContext):
    with session_scope() as s:
        ensure_drills_in_db(s)
        u = s.query(User).filter_by(tg_id=m.from_user.id).first()
        if not u:
            await m.answer("Сначала /start для онбординга.", reply_markup=main_menu())
            return
        drill = choose_drill_for_user(s, u)
    p = drill.payload_json
    await state.update_data(
        drill_id=p["id"], steps=p["steps"], idx=0, check_q=p["check_question"], markers=p["success_markers"]
    )
    await state.set_state(TrainingFlow.steps)
    await m.answer(
        f"Этюд: {p['title']}\nШаг 1/{len(p['steps'])}:\n{p['steps'][0]}",
        reply_markup=_step_keyboard()
    )


# ← НОВОЕ: команда /training
@router.message(Command("training"))
async def training_cmd(m: Message, state: FSMContext):
    return await training_entry(m, state)


# ← НОВОЕ: подстрахуемся, если эмодзи/пробелы отличаются
@router.message(lambda m: isinstance(m.text, str) and "Тренировка дня" in m.text)
async def training_fuzzy(m: Message, state: FSMContext):
    return await training_entry(m, state)


@router.callback_query(TrainingFlow.steps, F.data.in_({"step_next", "step_skip", "step_done"}))
async def steps_flow(cb: CallbackQuery, state: FSMContext):
    d = await state.get_data()
    steps = d["steps"]
    idx = int(d.get("idx", 0))

    if cb.data == "step_done":
        await state.set_state(TrainingFlow.reflect_selecting)
        # вопрос рефлексии
        await _safe_edit_text(cb.message, f"Рефлексия: {d['check_q']}")
        # клавиатура — отдельным сообщением
        await cb.message.answer("Отметьте, что произошло:", reply_markup=_reflect_keyboard(set(), d["markers"]))
        await cb.answer()
        return

    # next / skip
    idx = idx + 1 if cb.data == "step_next" else idx + 2
    if idx >= len(steps):
        idx = len(steps) - 1
    await state.update_data(idx=idx)

    await _safe_edit_text(
        cb.message,
        f"Шаг {idx+1}/{len(steps)}:\n{steps[idx]}",
        reply_markup=_step_keyboard()
    )
    await cb.answer()


@router.callback_query(TrainingFlow.reflect_selecting, F.data.startswith("mk_"))
async def reflect_markers(cb: CallbackQuery, state: FSMContext):
    d = await state.get_data()
    selected = set(d.get("selected", set()))
    markers = d["markers"]

    if cb.data == "mk_save":
        success = len(selected) >= 2
        run_id: int | None = None  # <-- НОВОЕ: сохраним id прогона для ссылки в фидбэке
        with session_scope() as s:
            u = s.query(User).filter_by(tg_id=cb.from_user.id).first()
            if u:
                run = DrillRun(
                    user_id=u.id,
                    drill_id=d["drill_id"],
                    result_json={"selected": list(selected)},
                    success_bool=success,
                )
                s.add(run)
                u.streak = (u.streak or 0) + 1
                s.commit()
                run_id = run.id  # получаем id после commit

        await state.clear()
        verdict = "успех" if success else "нужно ещё разок"
        await cb.message.answer(f"Сохранено: {verdict}. Стрик +1. 🎉", reply_markup=main_menu())

        # <-- НОВОЕ: приглашение к отзыву
        if run_id is not None:
            await cb.message.answer(
                "Как прошёл этюд? Оцените или оставьте краткий отзыв:",
                reply_markup=feedback_kb("training", str(run_id)),
            )

        await cb.answer()
        return

    # переключение маркера
    _, ixs = cb.data.split("_", 1)
    i = int(ixs)
    if 0 <= i < len(markers):
        if markers[i] in selected:
            selected.remove(markers[i])
        else:
            selected.add(markers[i])

    await state.update_data(selected=selected)

    # обновляем только клавиатуру, но аккуратно
    try:
        await cb.message.edit_reply_markup(reply_markup=_reflect_keyboard(selected, markers))
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e).lower():
            raise
    await cb.answer()
