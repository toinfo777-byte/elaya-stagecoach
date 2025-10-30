# app/routers/entrypoints.py
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils.deep_linking import create_start_link

from app.keyboards.main import main_kb

router = Router(name="entrypoints")


def _is_private(msg: Message) -> bool:
    return msg.chat.type == "private"


@router.message(F.text == "/start")
async def cmd_start(msg: Message):
    # В группах — полностью тихо, даже без клавиатуры
    if not _is_private(msg):
        return

    await msg.answer(
        "Привет! Я «Элайя — Тренер сцены». "
        "Нажми /menu, чтобы открыть разделы.",
        reply_markup=ReplyKeyboardRemove(),
    )


@router.message(F.text == "/menu")
async def cmd_menu(msg: Message):
    if _is_private(msg):
        # Только в личке показываем клавиатуру
        await msg.answer("Команды и разделы: выбери нужное ⤵️", reply_markup=main_kb())
        return

    # В группах не открываем клавиатуру и даем удобную ссылку в ЛС
    try:
        # deep-link на личный чат с ботом
        link = await create_start_link(msg.bot, payload="open_menu")
        text = (
            "Меню доступно в личном чате с ботом.\n"
            f"Открой: {link}"
        )
    except Exception:
        text = "Меню доступно в личном чате с ботом."

    await msg.answer(text, reply_markup=ReplyKeyboardRemove())


# На всякий случай: если кто-то шлёт «/help» в группе — без клавиатуры
@router.message(F.text.in_({"/help", "Помощь", "FAQ", "/faq"}))
async def cmd_help(msg: Message):
    if _is_private(msg):
        await msg.answer(
            "Помощь:\n"
            "• /menu — открыть разделы\n"
            "• Тренировка дня — ежедневная рутина 5–15 мин.\n"
            "• Мой прогресс — стрик и эпизоды за 7 дней.\n",
            reply_markup=ReplyKeyboardRemove(),
        )
        return

    await msg.answer("Помощь доступна в ЛС с ботом.", reply_markup=ReplyKeyboardRemove())
