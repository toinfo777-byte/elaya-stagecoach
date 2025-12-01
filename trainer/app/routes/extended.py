# trainer/app/routes/extended.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.types import Message

router = Router(name="extended")


# обработка кнопки или текста "Расширенная версия"
@router.message(F.text.contains("Расширенная версия"))
async def extended_version(message: Message) -> None:
    text = (
        "⭐️ Расширенная версия Элайи-Тренера — это будущий уровень.\n\n"
        "В ней появятся:\n"
        "• персональные сценарии тренировок;\n"
        "• более детальный дневник практики;\n"
        "• напоминания и мягкие «пинки» по ритму дня;\n"
        "• более глубокая связка с ядром Элайи.\n\n"
        "Сейчас расширенная версия в разработке.\n"
        "Когда она будет готова — ты узнаешь об этом первым прямо здесь. 🙂"
    )

    await message.answer(text)
