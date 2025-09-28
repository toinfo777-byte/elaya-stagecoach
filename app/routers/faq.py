from __future__ import annotations

import os
import time
import logging
import importlib
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

router = Router(name="faq")
log = logging.getLogger("faq")

# ──────────────────────────────────────────────────────────────────────────────
# Конфиг / окружение
# ──────────────────────────────────────────────────────────────────────────────

def _get_admin_ids_from_env() -> List[int]:
    ids = os.environ.get("ADMIN_IDS") or os.environ.get("ADMIN_ID") or ""
    out: List[int] = []
    for part in ids.replace(";", ",").split(","):
        part = part.strip()
        if not part:
            continue
        try:
            out.append(int(part))
        except ValueError:
            pass
    return out

ADMIN_ALERT_CHAT_ID: Optional[int] = None
try:
    # если есть settings, берём оттуда
    settings_mod = importlib.import_module("app.config")
    settings = getattr(settings_mod, "settings", None)
    ADMIN_ALERT_CHAT_ID = getattr(settings, "admin_alert_chat_id", None)
except Exception:
    settings = None

if not ADMIN_ALERT_CHAT_ID:
    val = os.environ.get("ADMIN_ALERT_CHAT_ID")
    ADMIN_ALERT_CHAT_ID = int(val) if val and val.isdigit() else None

ADMIN_IDS = set(_get_admin_ids_from_env())

RATE_LIMIT_SEC = 60  # отчёт об ошибке не чаще 1 раза в 60 секунд
_last_bug_report_ts: Dict[int, float] = {}

# ──────────────────────────────────────────────────────────────────────────────
# Контент FAQ: YAML (если есть) или дефолт
# ──────────────────────────────────────────────────────────────────────────────

_DEFAULT_FAQ = {
    "root_title": "❓ FAQ / помощь",
    "sections": [
        {
            "key": "FAQ_START",
            "title": "🚀 Как начать",
            "text": (
                "Нажми <b>Тренировка дня</b> — 1 минута практики.\n"
                "Затем <b>Мини-кастинг</b> — короткий «прогон».\n"
                "Если есть время — <b>Путь лидера</b> (чуть длиннее).\n"
                "Совет: одно слово-итог после практики — в комментарии: "
                "ровнее / теплее / острее / то же."
            ),
        },
        {
            "key": "FAQ_BUTTONS",
            "title": "🧭 Кнопки бота",
            "text": (
                "<b>Тренировка дня</b> — 1 мин., один приём внимания.\n"
                "<b>Мини-кастинг</b> — «сцена на 2–3 мин» из приёмов.\n"
                "<b>Путь лидера</b> — серия шагов/ритм на неделю.\n"
                "<b>FAQ / помощь</b> — ответы и связь.\n"
                "<b>Настройки</b> — уведомления, язык (в будущем)."
            ),
        },
        {
            "key": "FAQ_NOTIFY",
            "title": "⏰ Уведомления / «тихо»",
            "text": (
                "Включить/выключить — <b>Настройки → Уведомления</b>.\n"
                "Время пуша — по умолчанию в <b>09:00</b>.\n"
                "Команда: <code>/notify_on</code>, "
                "<code>/notify_off</code>, "
                "<code>/notify_time 09:00</code>."
            ),
            "buttons": [
                {"text": "Вкл уведомления", "cb": "FAQ_NOTIFY_ON"},
                {"text": "Выкл", "cb": "FAQ_NOTIFY_OFF"},
                {"text": "Изменить время", "cb": "FAQ_NOTIFY_TIME"},
            ],
        },
        {
            "key": "FAQ_RESET",
            "title": "🧹 Сброс и очистка прогресса",
            "text": (
                "Сбросить текущий сценарий: <code>/reset</code>.\n"
                "Полная очистка (данные + прогресс): <code>/wipe</code>.\n"
                "<b>Внимание:</b> /wipe необратим."
            ),
        },
        {
            "key": "FAQ_ERRORS",
            "title": "🧑‍💻 Частые ошибки и решения",
            "text": (
                "Бот «молчит»: нажмите <code>/start</code> в этом чате.\n"
                "Кнопка не работает: обновите Telegram, попробуйте ещё раз.\n"
                "«Слишком много запросов»: подождите 30 сек.\n"
                "«Нет ссылки» / «404»: повторите из меню. Не помогло? → "
                "🐞 <b>Сообщить о проблеме</b>."
            ),
        },
        {
            "key": "FAQ_PRIVACY",
            "title": "🔒 Конфиденциальность и данные",
            "text": (
                "Мы храним минимум: ID и тех.метки шагов.\n"
                "Контент практик остаётся у вас.\n"
                "Удалить всё: <code>/wipe</code>.\n"
                "Запрос на выгрузку данных: <code>/export</code> "
                "(будет отправлен админам)."
            ),
        },
        {
            "key": "FAQ_CONTACT",
            "title": "💬 Задать вопрос Элайе / Связь с нами",
            "text": (
                "Вопрос Элайе: <code>/ask</code> ваш вопрос. "
                "Ответ придёт в этом чате.\n"
                "Связь с живым куратором: напишите сюда — "
                "мы ответим как сможем."
            ),
        },
        {
            "key": "FAQ_BUG",
            "title": "🐞 Сообщить о проблеме",
            "text": (
                "Нажмите кнопку ниже — мы получим техлоги и ваш комментарий.\n"
                "Опишите коротко: что нажали / что ожидали / что произошло."
            ),
            "buttons": [
                {"text": "Отправить отчёт", "cb": "FAQ_BUG_REPORT"},
            ],
        },
    ],
}

_FAQ: Dict[str, Any] = _DEFAULT_FAQ

def _try_load_yaml() -> None:
    """Пробуем загрузить app/content/faq_ru.yaml (если есть)."""
    global _FAQ
    path = os.path.join(os.path.dirname(__file__), "..", "content", "faq_ru.yaml")
    path = os.path.normpath(path)
    try:
        import yaml  # type: ignore
    except Exception:
        log.info("FAQ: PyYAML не установлен — используем дефолтные тексты.")
        return
    if not os.path.exists(path):
        log.info("FAQ: yaml не найден (%s) — используем дефолт.", path)
        return
    try:
        with open(path, "r", encoding="utf-8") as f:
            _FAQ = yaml.safe_load(f) or _DEFAULT_FAQ
        log.info("FAQ: yaml загружен (%s).", path)
    except Exception as e:
        log.warning("FAQ: не удалось прочитать yaml: %s — используем дефолт.", e)
        _FAQ = _DEFAULT_FAQ

_try_load_yaml()

# ──────────────────────────────────────────────────────────────────────────────
# Утилиты
# ──────────────────────────────────────────────────────────────────────────────

def _kb_nav(extra: List[List[InlineKeyboardButton]] | None = None) -> InlineKeyboardMarkup:
    # Навигация: Назад (к корню) и Домой (в меню)
    rows: List[List[InlineKeyboardButton]] = []
    if extra:
        rows.extend(extra)
    rows.append([
        InlineKeyboardButton(text="◀️ Назад", callback_data="FAQ_ROOT"),
        InlineKeyboardButton(text="🏠 В меню", callback_data="go:menu"),
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def _kb_root() -> InlineKeyboardMarkup:
    rows: List[List[InlineKeyboardButton]] = []
    # 8 разделов из ТЗ в порядке
    order = [
        "FAQ_START","FAQ_BUTTONS","FAQ_NOTIFY","FAQ_RESET",
        "FAQ_ERRORS","FAQ_PRIVACY","FAQ_CONTACT","FAQ_BUG"
    ]
    by_key = {s["key"]: s for s in _FAQ.get("sections", [])}
    for i in range(0, len(order), 2):
        row: List[InlineKeyboardButton] = []
        for key in order[i:i+2]:
            sec = by_key.get(key)
            if not sec:
                continue
            row.append(InlineKeyboardButton(text=sec["title"], callback_data=key))
        if row:
            rows.append(row)
    return _kb_nav(rows)

async def _answer_or_edit(obj: Message | CallbackQuery, text: str, kb: InlineKeyboardMarkup):
    if isinstance(obj, CallbackQuery):
        try:
            await obj.message.edit_text(text, reply_markup=kb)
        except Exception:
            # если не удалось отредактировать — шлём новое
            await obj.message.answer(text, reply_markup=kb)
    else:
        await obj.answer(text, reply_markup=kb)

def _render_section_text(key: str) -> tuple[str, InlineKeyboardMarkup]:
    # Находим секцию по ключу
    by_key = {s["key"]: s for s in _FAQ.get("sections", [])}
    sec = by_key.get(key)
    if not sec:
        return ("Раздел временно недоступен.", _kb_nav())
    text = f"<b>{sec['title']}</b>\n\n{sec['text']}"
    extra_rows: List[List[InlineKeyboardButton]] = []
    for btn in sec.get("buttons", []) or []:
        extra_rows.append([InlineKeyboardButton(text=btn["text"], callback_data=btn["cb"])])
    return (text, _kb_nav(extra_rows) if extra_rows else _kb_nav())

def _track(event: str, user_id: int, **meta: Any) -> None:
    log.info("analytics: %s uid=%s meta=%s", event, user_id, meta)

# ──────────────────────────────────────────────────────────────────────────────
# Публичные функции
# ──────────────────────────────────────────────────────────────────────────────

async def show_faq_root(obj: Message | CallbackQuery) -> None:
    """Открыть корневой экран FAQ (используется из entrypoints)."""
    title = _FAQ.get("root_title", "❓ FAQ / помощь")
    text = f"{title}\n\nВыберите раздел:"
    await _answer_or_edit(obj, text, _kb_root())
    uid = obj.from_user.id if isinstance(obj, (Message, CallbackQuery)) else 0
    _track("faq_open", uid)

# ──────────────────────────────────────────────────────────────────────────────
# Обработчики команд
# ──────────────────────────────────────────────────────────────────────────────

@router.message(StateFilter("*"), Command("help"))
async def cmd_help(m: Message):
    await show_faq_root(m)
    _track("help_command_used", m.from_user.id)

@router.message(Command("notify_on"))
async def cmd_notify_on(m: Message):
    # здесь должна быть реальная запись в профиль; MVP — подтверждение
    await m.answer("🔔 Уведомления: <b>включены</b>.", parse_mode="HTML")
    _track("faq_notify_on", m.from_user.id)

@router.message(Command("notify_off"))
async def cmd_notify_off(m: Message):
    await m.answer("🔕 Уведомления: <b>выключены</b>.", parse_mode="HTML")
    _track("faq_notify_off", m.from_user.id)

class FAQStates(StatesGroup):
    wait_time = State()
    wait_bug = State()

@router.message(Command("notify_time"))
async def cmd_notify_time(m: Message, state: FSMContext):
    # ожидаем формат /notify_time HH:MM
    parts = (m.text or "").split(maxsplit=1)
    if len(parts) == 2:
        hhmm = parts[1].strip()
        await m.answer(f"⏰ Время напоминаний установлено на <b>{hhmm}</b>.", parse_mode="HTML")
        _track("faq_notify_time_set", m.from_user.id, time=hhmm)
        return
    await m.answer("Укажи время в формате <code>/notify_time HH:MM</code> (например, 09:00).", parse_mode="HTML")

@router.message(Command("ask"))
async def cmd_ask(m: Message):
    parts = (m.text or "").split(maxsplit=1)
    if len(parts) < 2:
        await m.answer("Отправь вопрос в формате: <code>/ask твой вопрос</code>.", parse_mode="HTML")
        return
    question = parts[1]
    await m.answer("Спасибо! Элайя ответит в этом чате. (MVP)")  # здесь можно подключить вашу логику Q&A
    _track("faq_ask_sent", m.from_user.id)

@router.message(Command("faq_reload"))
async def cmd_faq_reload(m: Message):
    if m.from_user.id not in ADMIN_IDS:
        return
    _try_load_yaml()
    await m.answer("FAQ: конфигурация перечитана.")
    _track("faq_reload", m.from_user.id)

# ──────────────────────────────────────────────────────────────────────────────
# Колбэки разделов
# ──────────────────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "FAQ_ROOT")
async def cb_root(cb: CallbackQuery):
    await show_faq_root(cb)

@router.callback_query(F.data.in_({
    "FAQ_START","FAQ_BUTTONS","FAQ_NOTIFY","FAQ_RESET",
    "FAQ_ERRORS","FAQ_PRIVACY","FAQ_CONTACT","FAQ_BUG"
}))
async def cb_section(cb: CallbackQuery):
    text, kb = _render_section_text(cb.data)
    await _answer_or_edit(cb, text, kb)
    _track("faq_section_open", cb.from_user.id, section=cb.data)

# ──────────────────────────────────────────────────────────────────────────────
# Спец-кнопки разделов
# ──────────────────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "FAQ_NOTIFY_ON")
async def cb_notify_on(cb: CallbackQuery):
    await cb.answer()
    await cb.message.answer("🔔 Уведомления: <b>включены</b>.", parse_mode="HTML")
    _track("faq_notify_on", cb.from_user.id)

@router.callback_query(F.data == "FAQ_NOTIFY_OFF")
async def cb_notify_off(cb: CallbackQuery):
    await cb.answer()
    await cb.message.answer("🔕 Уведомления: <b>выключены</b>.", parse_mode="HTML")
    _track("faq_notify_off", cb.from_user.id)

@router.callback_query(F.data == "FAQ_NOTIFY_TIME")
async def cb_notify_time(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await cb.message.answer("Укажи время: <code>/notify_time HH:MM</code> (например, 09:00).", parse_mode="HTML")
    _track("faq_notify_time_click", cb.from_user.id)

@router.callback_query(F.data == "FAQ_BUG_REPORT")
async def cb_bug_start(cb: CallbackQuery, state: FSMContext):
    uid = cb.from_user.id
    now = time.time()
    last = _last_bug_report_ts.get(uid, 0)
    if now - last < RATE_LIMIT_SEC:
        await cb.answer("Слишком часто. Попробуйте позже.", show_alert=True)
        return
    _last_bug_report_ts[uid] = now

    await state.set_state(FAQStates.wait_bug)
    await cb.message.answer("Коротко опиши проблему одной фразой (или пришли скрин).")
    _track("faq_bug_start", uid)

@router.message(StateFilter(FAQStates.wait_bug))
async def on_bug_text(m: Message, state: FSMContext):
    await state.clear()
    text = m.text or "(без текста)"
    uid = m.from_user.id
    uname = (m.from_user.username and f"@{m.from_user.username}") or ""
    when = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    alert = (
        f"🐞 <b>Bug report</b>\n"
        f"👤 id: <code>{uid}</code> {uname}\n"
        f"🕒 {when}\n"
        f"📝 {text}"
    )
    if ADMIN_ALERT_CHAT_ID:
        try:
            await m.bot.send_message(ADMIN_ALERT_CHAT_ID, alert, parse_mode="HTML")
        except Exception as e:
            log.warning("Не удалось отправить отчёт админу: %s", e)

    await m.answer("Спасибо! Отчёт отправлен. Мы посмотрим как можно быстрее.")
    _track("bug_report_sent", uid)
