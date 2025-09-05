# app/routers/system.py
from datetime import datetime, timezone
from aiogram import Router, F, types
from aiogram.filters import Command
from app.config import settings
from app.storage.repo import session_scope
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
    # короткий вид: d hh:mm:ss
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
