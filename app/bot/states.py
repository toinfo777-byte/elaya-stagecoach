from aiogram.fsm.state import State, StatesGroup

class CoachStates(StatesGroup):
    wait_feeling = State()

class FeedbackStates(StatesGroup):
    wait_phrase = State()
