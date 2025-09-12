from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

router = Router(name="settings")

# — маленький хелпер: матч по подстроке без учёта регистра (и с эмодзи в начале)
def _contains(substr: str):
    return F.text.func(lambda t: isinstance(t, str) and substr.lower() in t.lower())

# ===== Команда /settings и кнопка «Настройки» =====
@router.message(F.text == "/settings")
@router.message(_contains("Настройки"))
async def settings_entry(msg: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧹 Удалить профиль", callback_data="settings:delete")],
        [InlineKeyboardButton(text="↩️ В меню", callback_data="settings:menu")],
    ])
    await msg.answer(
        "⚙️ Настройки.\n\nМожешь удалить профиль или вернуться в меню.",
        reply_markup=kb,
    )

# ===== Удаление профиля: подтверждение =====
@router.callback_query(F.data == "settings:delete")
async def settings_delete_confirm(cb: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Да, удалить", callback_data="settings:delete:yes"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="settings:delete:no"),
        ]
    ])
    await cb.message.edit_text(
        "🧹 Удалить профиль? Это действие необратимо.",
        reply_markup=kb,
    )
    await cb.answer()

# ===== Удаление профиля: да/нет =====
@router.callback_query(F.data == "settings:delete:no")
async def settings_delete_no(cb: CallbackQuery):
    await cb.message.edit_text("Отменено. Никуда не делись 🙂")
    await cb.answer()

@router.callback_query(F.data == "settings:delete:yes")
async def settings_delete_yes(cb: CallbackQuery):
    # Здесь можно вставить реальное удаление из БД, если нужно.
    # Например: await repo.delete_user(cb.from_user.id)
    await cb.message.edit_text("✅ Профиль удалён. Если передумаешь — напиши /start.")
    await cb.answer()

# ===== «В меню» (инлайн из настроек) =====
@router.callback_query(F.data == "settings:menu")
async def settings_to_menu(cb: CallbackQuery):
    # просто подсказываем команду — твоё меню уже делает остальное
    await cb.message.edit_text("Ок! Открой меню: /menu")
    await cb.answer()

# ===== На случай, если кнопку «Удалить профиль» сделали reply-кнопкой =====
@router.message(_contains("Удалить профиль"))
async def settings_delete_from_reply_button(msg: Message):
    # Переиспользуем логику подтверждения через инлайн
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Да, удалить", callback_data="settings:delete:yes"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="settings:delete:no"),
        ]
    ])
    await msg.answer("🧹 Удалить профиль? Это действие необратимо.", reply_markup=kb)
