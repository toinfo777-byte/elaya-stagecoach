# app/routers/trainer.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from app.keyboards.reply import main_menu_kb, BTN_TRAINING
from app import core_api  # ✅ исправлено: относительный импорт к StageCoach

router = Router(name="trainer")

SCENE_NAME = "training_demo"  # любое имя для статистики в HQ


# --- вход в тренировку --------------------------------------------------------
async def _training_entry(m: Message) -> None:
    # обращаемся к ядру (scene_enter)
    try:
        reply = await core_api.scene_enter(
            user_id=m.from_user.id,
            chat_id=m.chat.id,
            scene=SCENE_NAME,
        )
    except Exception as e:
        reply = f"⚠️ Ошибка подключения к ядру: {e}"

    await m.answer(
        reply or "Тренировка дня:\n\n• «Пауза 2 секунды»\n• «Ровный тембр»",
        reply_markup=main_menu_kb(),
    )


# совместимость со старым названием
async def show_training_levels(m: Message) -> None:
    await _training_entry(m)


@router.message(Command("training", "levels", "уровни"))
async def cmd_training(m: Message) -> None:
    await _training_entry(m)


@router.message(F.text == BTN_TRAINING)
async def btn_training(m: Message) -> None:
    await _training_entry(m)


# --- отражение (рефлексия) ----------------------------------------------------
@router.message(F.text & ~F.text.in_({BTN_TRAINING}))
async def on_reflect(m: Message) -> None:
    """
    Любой осмысленный текст пользователя трактуем как рефлексию.
    Она отправляется в ядро StageCoach → сохраняется в /data/elaya.db.
    """
    try:
        reply = await core_api.scene_reflect(
            user_id=m.from_user.id,
            chat_id=m.chat.id,
            scene=SCENE_NAME,
            text=m.text,
        )
    except Exception as e:
        reply = f"⚠️ Ошибка связи с HQ: {e}"

    await m.answer(reply or "✅ Принято.")


# --- переход между сценами ----------------------------------------------------
@router.message(Command("next"))
async def cmd_next(m: Message) -> None:
    try:
        reply = await core_api.scene_transition(
            user_id=m.from_user.id,
            chat_id=m.chat.id,
            scene=SCENE_NAME,
        )
    except Exception as e:
        reply = f"⚠️ Ошибка связи с HQ: {e}"

    await m.answer(reply or "Следующий шаг.")
