# app/bot/states.py
from aiogram.fsm.state import StatesGroup, State

class FeedbackStates(StatesGroup):
    # ждём короткий текст отзыва
    wait_text = State()
