# app/bot/states.py
from aiogram.fsm.state import StatesGroup, State

class FeedbackStates(StatesGroup):
    wait_phrase = State()
