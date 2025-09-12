# app/bot/states.py
from aiogram.fsm.state import State, StatesGroup

class CoachStates(StatesGroup):
    wait_feeling = State()   # ждём одно слово после таймера
