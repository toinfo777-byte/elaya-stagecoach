# 🩵 Elaya StageCoach — Миграция staging на webhook

**Дата:** 28 октября 2025  
**Причина:** неустранимый TelegramConflictError при polling  
**Решение:** staging переведён на webhook-режим через `elaya-stagecoach-web`  

---

### ⚙️ Техническое действие
- MODE: `webhook`
- BOT_TOKEN: токен `ElayaStagingBot`
- WEBHOOK_BASE: `https://elaya-stagecoach-web.onrender.com`
- WEBHOOK_PATH: `/tg/<secret>`
- Сервис staging-worker: **отключён**
- Сервис web: принимает апдейты Telegram и статус-запросы `/status_json`

---

### 🧩 Результат
- Конфликт polling устранён.
- Telegram webhook активен: `✅ setWebhook: https://.../tg/<secret>`
- В логах Render — стабильные `POST /tg/... 200`.
- Все команды staging-бота выполняются мгновенно.

---

### 🧭 Следующие шаги
1. 📤 Отправлены запросы в Render Support и Telegram Bot Support для диагностики возможного «залипания» getUpdates.
2. 🧱 Подготовка отдельного воркера для будущего QA-бота (через webhook).
3. 🧩 Обновление `Elaya_Status_Q4_2025.md`: отметка «Инцидент закрыт, система стабильна».

---

_Документ составлен автоматически на основе миграционного плана 28.10.2025._
