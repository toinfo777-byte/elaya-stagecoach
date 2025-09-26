# app/routers/entrypoints.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.filters.command import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from app.keyboards.reply import (
    main_menu_kb,
    BTN_TRAINING, BTN_CASTING, BTN_APPLY, BTN_PROGRESS,
)

# профильные точки входа
from app.routers.training import show_training_levels  # публичный entry
from app.routers.minicasting import start_minicasting  # публичный entry
from app.routers.progress import show_progress         # публичный entry

router = Router(name="entrypoints")


async def _show_main_menu(target: Message | CallbackQuery, greet: bool = False) -> None:
    if isinstance(target, CallbackQuery):
        await target.answer()
        m = target.message
    else:
        m = target
    if greet:
        await m.answer("Привет! Я Элайя — тренер сцены. Помогу прокачать голос и уверенность.")
    await m.answer("Готово! Открываю меню.", reply_markup=main_menu_kb())


# ===== Команды «всегда работают» =====
@router.message(StateFilter("*"), Command("menu", "start", "cancel"))
async def ep_menu_cmd(m: Message, state: FSMContext):
    await state.clear()
    await _show_main_menu(m, greet=("start" in (m.text or "").lower()))


# ===== Текстовые кнопки Reply-клавиатуры =====
@router.message(StateFilter("*"), F.text.in_({"🏠 В меню", "Меню", "В меню"}))
async def ep_menu_btn(m: Message, state: FSMContext):
    await state.clear()
    await _show_main_menu(m)

@router.message(StateFilter("*"), F.text == BTN_TRAINING)
async def ep_training_btn(m: Message, state: FSMContext):
    await state.clear()
    await show_training_levels(m, state)

@router.message(StateFilter("*"), F.text == BTN_CASTING)
async def ep_casting_btn(m: Message, state: FSMContext):
    await state.clear()
    await start_minicasting(m, state)

@router.message(StateFilter("*"), F.text == BTN_APPLY)
async def ep_apply_btn(m: Message, state: FSMContext):
    await state.clear()
    # единая точка входа «Путь лидера»
    from app.routers.leader import start_leader_cmd
    await start_leader_cmd(m, state)

@router.message(StateFilter("*"), F.text == BTN_PROGRESS)
async def ep_progress_btn(m: Message, state: FSMContext):
    await state.clear()
    await show_progress(m)


# ===== go:* колбэки из инлайн-меню/хелпа =====
@router.callback_query(StateFilter("*"), F.data == "go:menu")
async def ep_go_menu(cq: CallbackQuery, state: FSMContext):
    await state.clear()
    await _show_main_menu(cq)

@router.callback_query(StateFilter("*"), F.data == "go:training")
async def ep_go_training(cq: CallbackQuery, state: FSMContext):
    await state.clear()
    await cq.answer()
    await show_training_levels(cq.message, state)

@router.callback_query(StateFilter("*"), F.data == "go:casting")
async def ep_go_casting(cq: CallbackQuery, state: FSMContext):
    await state.clear()
    await cq.answer()
    await start_minicasting(cq, state)

@router.callback_query(StateFilter("*"), F.data == "go:progress")
async def ep_go_progress(cq: CallbackQuery, state: FSMContext):
    await state.clear()
    await cq.answer()
    await show_progress(cq.message)

@router.callback_query(StateFilter("*"), F.data == "go:apply")
async def ep_go_apply(cq: CallbackQuery, state: FSMContext):
    await state.clear()
    await cq.answer()
    from app.routers.leader import start_leader_cmd
    await start_leader_cmd(cq.message, state)


# ===== /start с диплинком =====
@router.message(StateFilter("*"), CommandStart(deep_link=True))
async def ep_start_deeplink(m: Message, command: CommandObject, state: FSMContext):
    payload = (command.args or "").strip().lower()
    await state.clear()
    if payload.startswith("go_training"):
        return await show_training_levels(m, state)
    if payload.startswith("go_casting"):
        return await start_minicasting(m, state)
    if payload.startswith("go_apply"):
        from app.routers.leader import start_leader_cmd
        return await start_leader_cmd(m, state)
    return await _show_main_menu(m, greet=True)


__all__ = ["router"]
