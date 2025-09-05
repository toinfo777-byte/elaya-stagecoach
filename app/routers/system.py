# app/routers/system.py
from datetime import datetime, timezone
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    CallbackQuery, BotCommand,
)
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from app.config import settings
from app.storage.repo import session_scope, delete_user_cascade
from app.storage.models import User

router = Router(name="system")

# время старта процесса — для uptime
STARTED_AT = datetime.now(timezone.utc)

HELP_TEXT = (
    "Я — «Элайя — тренер сцены».\n"
    "Команды:\n"
    "/start — начать онбординг\n"
    "/menu — открыть меню\n"
    "/training — тренировка дня\n"
    "/progress — мой прогресс\n"
    "/privacy — политика и как удалить данные\n"
    "/wipe_me — удалить мой профиль и записи\n"
    "\nПодсказки: кнопки внизу экрана, никакого HTML/Markdown."
)

PRIVACY_TEXT = (
    "🔐 Политика кратко\n"
    "• Храним минимум: id, имя/username, ответы онбординга, результаты тренировок.\n"
    "• Используем только для статистики и улучшения этюдов.\n"
    "• Можно удалить всё командой /wipe_me — профиль и записи стираются.\n"
    "• Контакты из «Мини-кастинга» передаются только нашей команде.\n"
    "• База локально на сервере, бэкап раз в день, хранение 7 дней.\n"
    "Вопросы — ответьте в чате, мы на связи."
)

VERSION = settings.version if getattr(settings, "version", None) else "dev"


def _uptime() -> str:
    delta = datetime.now(timezone.utc) - STARTED_AT
    secs = int(delta.total_seconds())
    d, secs = divmod(secs, 86400)
    h, secs = divmod(secs, 3600)
    m, s = divmod(secs, 60)
    if d:
        return f"{d}d {h:02}:{m:02}:{s:02}"
    return f"{h:02}:{m:02}:{s:02}"


@router.message(Command("help"))
async def help_cmd(m: types.Message):
    await m.answer(HELP_TEXT)


@router.message(Command("privacy"))
async def privacy_cmd(m: types.Message):
    await m.answer(PRIVACY_TEXT + "\n\nНапоминание: для стирания данных используйте /wipe_me")


@router.message(Command("health"))
async def health_cmd(m: types.Message):
    db_kind = "sqlite" if settings.db_url.startswith("sqlite") else "postgres"
    await m.answer(f"ok | env={settings.env} | db={db_kind} | uptime={_uptime()}")


@router.message(Command("version"))
async def version_cmd(m: types.Message):
    await m.answer(f"version: {VERSION}")


@router.message(Command("whoami"))
async def whoami_cmd(m: types.Message):
    uid = m.from_user.id
    is_admin = uid in settings.admin_ids
    un = f"@{m.from_user.username}" if m.from_user.username else "-"
    full = " ".join(filter(None, [m.from_user.first_name, m.from_user.last_name]))
    await m.answer(f"id={uid} | user={un} | name={full or '-'} | admin={is_admin}")


# ---------- /wipe_me: подтверждение и полное удаление ----------
class WipeFlow(StatesGroup):
    confirm = State()


def _wipe_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🗑 Удалить навсегда", callback_data="wipe_yes")],
        [InlineKeyboardButton(text="Отмена", callback_data="wipe_no")],
    ])


@router.message(Command("wipe_me"))
async def wipe_me_start(m: types.Message, state: FSMContext):
    await state.set_state(WipeFlow.confirm)
    await m.answer(
        "⚠️ Вы собираетесь удалить профиль и все связанные записи (этюды, тесты, события, лиды). "
        "Действие необратимо. Подтвердить?",
        reply_markup=_wipe_kb()
    )


@router.callback_query(WipeFlow.confirm, F.data.in_({"wipe_yes", "wipe_no"}))
async def wipe_me_confirm(cb: CallbackQuery, state: FSMContext):
    if cb.data == "wipe_no":
        await state.clear()
        await cb.message.edit_text("Отменено. Ничего не удалено.")
        await cb.answer()
        return

    # wipe_yes
    with session_scope() as s:
        u = s.query(User).filter_by(tg_id=cb.from_user.id).first()
        if u:
            delete_user_cascade(s, u.id)
    await state.clear()
    try:
        await cb.message.edit_text("Готово. Ваш профиль и записи удалены. Вы можете снова пройти /start.")
    except Exception:
        await cb.message.answer("Готово. Ваш профиль и записи удалены. Вы можете снова пройти /start.")
    await cb.answer()


# ---------- установка меню команд ----------
async def setup_commands(bot):
    """Установить команды в меню бота."""
    cmds = [
        BotCommand(command="start", description="Начать онбординг"),
        BotCommand(command="menu", description="Открыть меню"),
        BotCommand(command="training", description="Тренировка дня"),
        BotCommand(command="progress", description="Мой прогресс"),
        BotCommand(command="help", description="Справка"),
        BotCommand(command="privacy", description="Политика"),
        BotCommand(command="wipe_me", description="Удалить профиль"),
    ]
    await bot.set_my_commands(cmds)
