# app/keyboards/inline.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# === КАСТИНГ: пропуск ссылки на портфолио =========================
def casting_skip_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Пропустить", callback_data="cast:skip_url")]
        ]
    )

# === МИНИ-КАСТИНГ: блок оценки (эмодзи + пропуск) =================
def mc_feedback_kb() -> InlineKeyboardMarkup:
    # Совместим с текущими fb:* и добавим альтернативные payload'ы на будущее
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔥", callback_data="fb:fire"),
            InlineKeyboardButton(text="👌", callback_data="fb:ok"),
            InlineKeyboardButton(text="😐", callback_data="fb:meh"),
        ],
        [InlineKeyboardButton(text="Пропустить", callback_data="mc:skip")],
    ])

# === ПУТЬ ЛИДЕРА: выбор намерения + «В меню» ======================
def leader_intent_kb() -> InlineKeyboardMarkup:
    def btn(text: str, payload: str) -> InlineKeyboardButton:
        return InlineKeyboardButton(text=text, callback_data=payload)
    return InlineKeyboardMarkup(inline_keyboard=[
        [btn("Голос", "leader:intent:voice")],
        [btn("Публичные выступления", "leader:intent:public")],
        [btn("Сцена", "leader:intent:stage")],
        [btn("Другое", "leader:intent:other")],
        [btn("В меню", "leader:menu")],
    ])

def leader_skip_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Пропустить", callback_data="leader:skip")],
        [InlineKeyboardButton(text="В меню", callback_data="leader:menu")],
    ])
