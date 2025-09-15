# app/bot/states.py
from aiogram.fsm.state import StatesGroup, State

class CoachStates(StatesGroup):
    wait_feeling = State()

class FeedbackStates(StatesGroup):
    wait_text = State()
