# app/routers/reply_shortcuts.py
from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

router = Router(name="reply_shortcuts")

def _contains(substr: str):
    """Подстрока без учёта регистра (работает и если в начале эмодзи)."""
    return F.text.func(lambda t: isinstance(t, str) and substr.lower() in t.lower())

# ---------- НАСТРОЙКИ ----------
@router.message(StateFilter("*"), _contains("Настройки"))
async def r_settings(msg: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧹 Удалить профиль", callback_data="settings:delete")],
        [InlineKeyboardButton(text="↩️ В меню", callback_data="settings:menu")],
    ])
    await msg.answer("⚙️ Настройки.\n\nМожешь удалить профиль или вернуться в меню.", reply_markup=kb)

@router.message(StateFilter("*"), _contains("Удалить профиль"))
async def r_settings_delete(msg: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Да, удалить", callback_data="settings:delete:yes"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="settings:delete:no"),
        ]
    ])
    await msg.answer("🧹 Удалить профиль? Это действие необратимо.", reply_markup=kb)

# ---------- ПРЕМИУМ ----------
@router.message(StateFilter("*"), _contains("Расширенная версия"))
async def r_premium(msg: Message):
    await msg.answer(
        "⭐ Расширенная версия\n\n"
        "• Больше сценариев тренировки\n"
        "• Персональные разборы\n"
        "• Расширенная метрика прогресса\n\n"
        "Пока это превью. Если интересно — напиши «Хочу расширенную» или жми /menu."
    )

@router.message(StateFilter("*"), _contains("Хочу расширенную"))
async def r_premium_lead(msg: Message):
    await msg.answer(
        "🔥 Супер! Мы свяжемся с тобой по контактам из анкеты. "
        "Если хочешь — оставь email или напиши /menu."
    )

# ---------- (опционально) ПОМОЩЬ/ПОЛИТИКА, если они тоже reply-кнопками ----------
@router.message(StateFilter("*"), _contains("Помощь"))
async def r_help(msg: Message):
    await msg.answer(
        "Команды:\n"
        "/start — начать и онбординг\n/menu — открыть меню\n/apply — Путь лидера (заявка)\n"
        "/training — тренировка дня\n/casting — мини-кастинг\n/coach_on — включить наставника\n"
        "/coach_off — выключить наставника\n/progress — мой прогресс\n/cancel — сбросить состояние\n"
        "/privacy — политика\n/version — версия бота\n/health — проверка статуса"
    )

@router.message(StateFilter("*"), _contains("Политика"))
async def r_privacy(msg: Message):
    await msg.answer("Политика конфиденциальности: мы бережно храним ваши данные и используем их только для работы бота.")
