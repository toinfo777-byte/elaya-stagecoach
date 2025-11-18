# 🚀 Вход в "Тренировку дня"
# Ловим любое сообщение, начинающееся с символа "🏋"
@router.message(F.text.startswith("🏋"))
async def start_training(message: Message, state: FSMContext) -> None:
    await state.clear()

    await send_timeline_event(
        "training:intro:start",
        {
            "user_id": message.from_user.id,
            "username": message.from_user.username,
        },
    )

    await message.answer(
        (
            "Начинаем <b>Тренировку дня</b>.\n\n"
            "1️⃣ <b>Вход в тело</b>\n"
            "Сделай пару спокойных вдохов и выдохов.\n"
            "Опиши в 1–3 предложениях, что сейчас ощущает твой голос и дыхание."
        ),
        reply_markup=ReplyKeyboardRemove(),
    )

    await state.set_state(TrainingFlow.intro)
