from __future__ import annotations

import logging
import importlib
from typing import Iterable, Awaitable

from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

log = logging.getLogger("panic")
router = Router(name="panic")

# ---------- UI: главное reply-меню (8 кнопок) ----------
def _main_kb() -> ReplyKeyboardMarkup:
    rows = [
        [KeyboardButton(text="🏋️ Тренировка дня"), KeyboardButton(text="📈 Мой прогресс")],
        [KeyboardButton(text="🎭 Мини-кастинг"),   KeyboardButton(text="🧭 Путь лидера")],
        [KeyboardButton(text="💬 Помощь / FAQ"),   KeyboardButton(text="⚙️ Настройки")],
        [KeyboardButton(text="🔐 Политика"),       KeyboardButton(text="⭐ Расширенная версия")],
    ]
    return ReplyKeyboardMarkup(
        keyboard=rows, resize_keyboard=True, is_persistent=True,
        input_field_placeholder="Выбери раздел…"
    )

MENU_TEXT = (
    "Команды и разделы: выбери нужное ⤵️\n\n"
    "🏋️ <b>Тренировка дня</b> — 5–15 мин.\n"
    "📈 <b>Мой прогресс</b> — стрик/эпизоды.\n"
    "🎭 <b>Мини-кастинг</b> • 🧭 <b>Путь лидера</b>\n"
    "💬 <b>Помощь / FAQ</b> • ⚙️ <b>Настройки</b>\n"
    "🔐 <b>Политика</b> • ⭐ <b>Расширенная версия</b>"
)

async def _menu(m: Message):
    await m.answer("·", reply_markup=ReplyKeyboardRemove())
    await m.answer(MENU_TEXT, reply_markup=_main_kb())

# ---------- утилиты ----------
def _norm(text: str | None) -> str:
    return (text or "").strip().lower()

async def _call_optional(module: str, candidates: Iterable[str], *args, **kwargs) -> bool:
    try:
        mod = importlib.import_module(module)
    except Exception:
        return False
    for name in candidates:
        fn = getattr(mod, name, None)
        if callable(fn):
            res = fn(*args, **kwargs)
            if isinstance(res, Awaitable):
                await res
            return True
    return False

def _log_incoming(m: Message):
    t = m.text or ""
    hexs = " ".join(f"{ord(c):04x}" for c in t)
    log.info("panic:text=%r hex=[%s]", t, hexs)

# ---------- команды (block=True, чтобы другие роутеры не перехватывали) ----------
@router.message(CommandStart(deep_link=False), flags={"block": True})
async def start(m: Message, state: FSMContext):
    _log_incoming(m)
    await _menu(m)

@router.message(Command("menu"), flags={"block": True})
async def cmd_menu(m: Message, state: FSMContext):
    _log_incoming(m)
    await _menu(m)

@router.message(Command("fixmenu"), flags={"block": True})
async def cmd_fixmenu(m: Message):
    _log_incoming(m)
    await _menu(m)

@router.message(Command("ping"), flags={"block": True})
async def ping(m: Message):
    _log_incoming(m)
    await m.answer("pong 🟢", reply_markup=_main_kb())

# ---------- Тренировка (встроено здесь) ----------
try:
    from app.storage.repo_extras import save_training_episode
except Exception:
    save_training_episode = None

LEVEL1_TEXT = (
    "Уровень 1 · 5 мин\n\n"
    "Дыхание — 1 мин: вдох 4 — пауза 2 — выдох 6 на «с».\n"
    "Рот/язык — 2 мин: трель по 20–30 сек; 10 щелчков.\n"
    "Артикуляция — 2 мин: «Шла Саша по шоссе…» с паузами (|)."
)
LEVEL2_TEXT = (
    "Уровень 2 · 10 мин\n\n"
    "Опора — 3 мин: вдох в бока, выдох «ф/с».\n"
    "Резонаторы — 3 мин: «м» на 3–5 нот.\n"
    "Текст-ритм — 4 мин: 1) ровно 2) «3-2-1» 3) акценты."
)
LEVEL3_TEXT = (
    "Уровень 3 · 15 мин (Про)\n\n"
    "Резонаторы — 5 мин: «м-н-нг», серии «би-бе-ба-бо-бу».\n"
    "Текст с паузами — 5 мин: 6–8 фраз, паузы 2|1|3|1|2|3.\n"
    "Микро-этюд — 5 мин: тезис → история 20–30 сек → вывод."
)

class TrState(StatesGroup):
    level = State()

def _levels_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Уровень 1"), KeyboardButton(text="Уровень 2")],
            [KeyboardButton(text="Уровень 3"), KeyboardButton(text="🏠 В меню")],
        ],
        resize_keyboard=True, input_field_placeholder="Выбери уровень…"
    )

def _done_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="✅ Выполнил(а)")], [KeyboardButton(text="🏠 В меню")]],
        resize_keyboard=True
    )

# мягкие фильтры по словам (а не по эмодзи/строке целиком)
@router.message(F.text.func(lambda t: t and "трениров" in t.lower()), flags={"block": True})
async def open_training(m: Message, state: FSMContext):
    _log_incoming(m)
    await state.clear()
    await m.answer(
        "🏋️ <b>Тренировка дня</b>\n\n"
        "Выбери уровень — внутри подробные шаги. Когда закончишь — жми «✅ Выполнил(а)». "
        "Вернуться — «🏠 В меню».", reply_markup=_levels_kb()
    )

@router.message(F.text.in_({"Уровень 1", "Уровень 2", "Уровень 3"}), flags={"block": True})
async def training_level(m: Message, state: FSMContext):
    _log_incoming(m)
    mp = {"Уровень 1": ("1", LEVEL1_TEXT), "Уровень 2": ("2", LEVEL2_TEXT), "Уровень 3": ("3", LEVEL3_TEXT)}
    lvl, txt = mp[m.text]
    await state.set_state(TrState.level)
    await state.update_data(level=lvl)
    await m.answer(txt, reply_markup=_done_kb())

@router.message(F.text.func(lambda t: t and "выполнил" in t.lower()), flags={"block": True})
async def training_done(m: Message, state: FSMContext):
    _log_incoming(m)
    data = await state.get_data()
    level = data.get("level")
    if not level:
        await m.answer("Сначала выбери уровень 🙌", reply_markup=_levels_kb()); return
    if save_training_episode:
        try:
            await save_training_episode(user_id=m.from_user.id, level=str(level))
            log.info("training: user=%s episode saved (level=%s)", m.from_user.id, level)
        except Exception as e:
            log.exception("training save failed: %s", e)
    else:
        log.warning("save_training_episode not available; progress not persisted")
    await m.answer("🔥 Отлично! День засчитан. Увидимся завтра!", reply_markup=_levels_kb())
    await state.clear()

# ---------- Остальные разделы: мягкий импорт + блокируем распространение ----------
@router.message(F.text.func(lambda t: t and "прогресс" in t.lower()), flags={"block": True})
async def open_progress(m: Message):
    _log_incoming(m)
    ok = await _call_optional("app.routers.progress", ("show_progress","open_progress"), m)
    if not ok:
        await m.answer("📈 Раздел «Мой прогресс» будет доступен позже.", reply_markup=_main_kb())

@router.message(F.text.func(lambda t: t and "мини" in t.lower()), flags={"block": True})
async def open_mc(m: Message, state: FSMContext):
    _log_incoming(m)
    ok = await _call_optional("app.routers.minicasting", ("open_minicasting","show_minicasting","mc_entry","start_minicasting"), m, state)
    if not ok:
        await m.answer("🎭 «Мини-кастинг» скоро будет доступен.", reply_markup=_main_kb())

@router.message(F.text.func(lambda t: t and "лидер" in t.lower()), flags={"block": True})
async def open_leader(m: Message, state: FSMContext):
    _log_incoming(m)
    ok = await _call_optional("app.routers.leader", ("open_leader","show_leader","leader_entry","start_leader"), m, state)
    if not ok:
        await m.answer("🧭 «Путь лидера» скоро будет доступен.", reply_markup=_main_kb())

@router.message(F.text.func(lambda t: t and ("помощ" in t.lower() or "faq" in t.lower())), flags={"block": True})
async def open_help(m: Message):
    _log_incoming(m)
    ok = await _call_optional("app.routers.help", ("show_help",), m)
    if not ok:
        ok = await _call_optional("app.routers.faq", ("open_faq","show_faq"), m)
    if not ok:
        await m.answer("💬 Раздел помощи обновим чуть позже.", reply_markup=_main_kb())

@router.message(F.text.func(lambda t: t and "настрой" in t.lower()), flags={"block": True})
async def open_settings(m: Message):
    _log_incoming(m)
    ok = await _call_optional("app.routers.settings", ("show_settings","open_settings"), m)
    if not ok:
        await m.answer("⚙️ Профиль скоро будет доступен.", reply_markup=_main_kb())

@router.message(F.text.func(lambda t: t and "политик" in t.lower()), flags={"block": True})
async def open_privacy(m: Message):
    _log_incoming(m)
    ok = await _call_optional("app.routers.privacy", ("show_privacy","open_privacy"), m)
    if not ok:
        await m.answer("🔐 Политика будет опубликована перед релизом.", reply_markup=_main_kb())

@router.message(F.text.func(lambda t: t and "расшир" in t.lower()), flags={"block": True})
async def open_extended(m: Message):
    _log_incoming(m)
    ok = await _call_optional("app.routers.extended", ("open_extended","show_extended","extended_entry"), m)
    if not ok:
        await m.answer("⭐️ «Расширенная версия» — позже.", reply_markup=_main_kb())

# ---------- fallback: любое другое сообщение → меню (и блок) ----------
@router.message(flags={"block": True})
async def fallback(m: Message):
    _log_incoming(m)
    await _menu(m)
