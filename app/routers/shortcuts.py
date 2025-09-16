# app/routers/shortcuts.py
from __future__ import annotations
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.routers.menu import (
    BTN_TRAIN, BTN_PROGRESS, BTN_APPLY, BTN_CASTING, BTN_HELP, BTN_POLICY, main_menu
)
from app.routers.training import training_entry
from app.routers.casting import casting_entry
from app.routers.apply import apply_entry
from app.routers.system import PRIVACY_TEXT, HELP_TEXT
from app.routers.progress import send_progress_card

router = Router(name="shortcuts")

# Команды, которые должны работать в любом состоянии
@router.message(StateFilter("*"), Command("training"))
async def sc_training_cmd(m: Message, state: FSMContext):
    await training_entry(m, state)

@router.message(StateFilter("*"), Command("casting"))
async def sc_casting_cmd(m: Message, state: FSMContext):
    await casting_entry(m, state)

@router.message(StateFilter("*"), Command("apply"))
async def sc_apply_cmd(m: Message, state: FSMContext):
    await apply_entry(m, state)

@router.message(StateFilter("*"), Command("progress"))
async def sc_progress_cmd(m: Message):
    await send_progress_card(m)

@router.message(StateFilter("*"), Command("privacy"))
async def sc_privacy_cmd(m: Message):
    await m.answer(PRIVACY_TEXT, reply_markup=main_menu())

@router.message(StateFilter("*"), Command("help"))
async def sc_help_cmd(m: Message):
    await m.answer(HELP_TEXT, reply_markup=main_menu())

# Кнопки нижнего меню — тоже в любом состоянии:
@router.message(StateFilter("*"), F.text == BTN_TRAIN)
async def sc_training_btn(m: Message, state: FSMContext):
    await training_entry(m, state)

@router.message(StateFilter("*"), F.text == BTN_CASTING)
async def sc_casting_btn(m: Message, state: FSMContext):
    await casting_entry(m, state)

@router.message(StateFilter("*"), F.text == BTN_APPLY)
async def sc_apply_btn(m: Message, state: FSMContext):
    await apply_entry(m, state)

@router.message(StateFilter("*"), F.text == BTN_PROGRESS)
async def sc_progress_btn(m: Message):
    await send_progress_card(m)

@router.message(StateFilter("*"), F.text == BTN_POLICY)
async def sc_policy_btn(m: Message):
    await m.answer(PRIVACY_TEXT, reply_markup=main_menu())

@router.message(StateFilter("*"), F.text == BTN_HELP)
async def sc_help_btn(m: Message):
    await m.answer(HELP_TEXT, reply_markup=main_menu())
