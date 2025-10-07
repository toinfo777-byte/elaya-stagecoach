from __future__ import annotations
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from app.keyboards.menu import main_menu, get_bot_commands, BTN_HELP, BTN_PRIVACY

router = Router(name="system")

def _build_help_text() -> str:
    cmds = get_bot_commands()
    lines = ["💬 <b>Помощь</b>", "", "Команды:"]
    for c in cmds:
        lines.append(f"<code>/{c.command}</code> — {c.description}")
    return "\n".join(lines)

PRIVACY_TEXT = (
    "🔐 <b>Политика конфиденциальности</b>\n\n"
    "Мы храним минимум данных: ваш Telegram ID и ответы внутри бота.\n"
    "Командой <code>/wipe_me</code> профиль и записи можно удалить.\n"
    "Данные отзывов и прогресса используются для улучшения продукта."
)

@router.message(Command("help"))
@router.message(F.text == BTN_HELP)
async def help_handler(m: Message):
    await m.answer(_build_help_text(), reply_markup=main_menu())

@router.message(Command("privacy"))
@router.message(F.text == BTN_PRIVACY)
async def privacy_handler(m: Message):
    await m.answer(PRIVACY_TEXT, reply_markup=main_menu())

@router.message(Command("version"))
async def version_handler(m: Message):
    await m.answer("version=dev tmp", reply_markup=main_menu())

# ВАЖНО: тут БОЛЬШЕ НЕТ обработчика @router.message(Command("menu"))
