# Elaya · Документация ядра

> Ветвь: `develop`  
> Цикл: Q4 · 2025  
> Статус: 🟢 Stable Core (Portal v0)

---

## 🌐 Структура документов

| Раздел | Файл | Назначение |
|---------|------|------------|
| 🧭 **Статус ядра** | [`Elaya_Current_Status_Q4_2025.md`](./Elaya_Current_Status_Q4_2025.md) | Текущее состояние системы: build-метки, окружения, приоритеты |
| 🎭 **Trainer Portal** | [`Trainer_Portal.md`](./Trainer_Portal.md) | Контракт между trainer-ботом и web-ядром, описание Core API и сцен |
| 📈 **HQ Pulse** | [`hq/pulse/`](./hq/pulse/) | Утренние отчёты и динамика системы (09:00 MSK) |
| 🌙 **Nightly Report** | [`hq/reports/`](./hq/reports/) | Ночные отчёты, итоговые события (23:59 MSK) |
| ⚙️ **DevOps / Workflows** | [`.github/workflows/`](../.github/workflows/) | Автоматические задачи GitHub Actions (cron, деплой, отчёты) |
| ⚡ **HQ · Принципы** | [`hq/HQ_Principle_Text_Generation.md`](./hq/HQ_Principle_Text_Generation.md) | Архитектурный принцип распределения смыслов между слоями |


---

## 🩶 Принципы штабной документации

1. **Минимум слов — максимум точности.**  
   Каждый файл должен быть читаем как отчёт инженеру, а не как эссе.

2. **Синхронность с реальностью.**  
   Любое изменение в Render, GitHub Actions или окружении отражается здесь в тот же день.

3. **Видимость — основа доверия.**  
   HQ-файлы всегда открыты в develop-ветке, чтобы любая часть системы могла видеть состояние другой.

4. **Тишина = норма.**  
   Если в отчётах нет ошибок и алёртов — значит система дышит ровно.  
   Любой сигнал (⚠️) требует фиксации причины и решения в этом же цикле.

---

## 🔁 Цикл Q4 2025

| Этап | Цель | Состояние |
|------|------|------------|
| Portal v0 | Тонкий Trainer ↔ Core API ↔ Web | ✅ Онлайн |
| HQ Pulse | Автоматический дневной отчёт | ✅ Активен |
| Nightly Report | Ночной лог синхронизации | ✅ Активен |
| SAFE Mode | Удержание алёртов на 24 ч после релиза | 🕒 До 08 ноя 2025 |

---

## 🪶 Контактная точка

- **Главный поток HQ:** `Elaya HQ Bot`  
- **Сервисы:**  
  - Web → [`elaya-stagecoach-web`](https://dashboard.render.com/web/srv-d3sudv3uibrs73aje1pg)  
  - Trainer → [`elaya-trainer-bot`](https://dashboard.render.com/web/srv-d450summcj7s73freimg)  
- **Основной репозиторий:** [toinfo777-byte/elaya-stagecoach](https://github.com/toinfo777-byte/elaya-stagecoach)

---

*Обновлено: 03 April 2026 · Elaya HQ · StageCoach Core
