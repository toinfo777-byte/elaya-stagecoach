# app/bot/states.py
from aiogram.fsm.state import StatesGroup, State

class Feedback(StatesGroup):
    WaitRating = State()  # ждём нажатия 🔥/👌/😐 или «1 фраза»
    WaitText = State()    # ждём текст отзыва или «Пропустить»
