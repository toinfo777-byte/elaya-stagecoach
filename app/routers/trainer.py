from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReplyKeyboardRemove

from app.build import BUILD_MARK

router = Router(name="trainer")

MENU_TEXT = (
    "🧭 Меню Элайи\n\n"
    "🏋️ Тренировка дня — 5–15 минут\n"
    "📈 Мой прогресс — стрики и эпизоды\n"
    "🎯 Мини-кастинг • 🧭 Путь лидера\n"
    "🆘 Помощь / FAQ • ⚙️ Настройки\n"
    "📜 Политика • ⭐ Расширенная версия"
)

@router.message(CommandStart())
async def trainer_start(msg: Message):
    # строго без прикреплённой клавиатуры, только текст
    await msg.answer("Привет! Это тренер Элайи.\n" + MENU_TEXT, reply_markup=ReplyKeyboardRemove())

@router.message(Command("menu"))
async def trainer_menu(msg: Message):
    await msg.answer(MENU_TEXT, reply_markup=ReplyKeyboardRemove())

@router.message(Command("healthz"))
async def trainer_health(msg: Message):
    await msg.answer("ok", reply_markup=ReplyKeyboardRemove())

@router.message(Command("status"))
async def trainer_status(msg: Message):
    me = await msg.bot.get_me()
    await msg.answer(
        "🟢 Trainer online · webhook\n"
        f"Bot: @{me.username}\n"
        f"Build: <code>{BUILD_MARK}</code>\n"
        "Status: ok ✅",
        reply_markup=ReplyKeyboardRemove()
    )

# заглушки разделов — можно разворачивать по мере готовности
@router.message(F.text.in_({"Тренировка", "Тренировка дня"}))
@router.message(Command("training"))
async def trainer_training(msg: Message):
    await msg.answer("🏋️ Тренировка: сегодня — мягкое дыхание + центр звезды (5–10 мин).", reply_markup=ReplyKeyboardRemove())

@router.message(Command("help"))
async def trainer_help(msg: Message):
    await msg.answer(
        "Помощь:\n"
        "• /menu — главное меню\n"
        "• /training — начать тренировку\n"
        "• /status — статус тренера\n"
        "• /healthz — быстрая проверка",
        reply_markup=ReplyKeyboardRemove()
    )
