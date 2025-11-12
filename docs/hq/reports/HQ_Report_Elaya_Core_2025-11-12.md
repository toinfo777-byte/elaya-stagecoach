# HQ Report — Elaya Core · 2025-11-12

**Статус:** ✅ Online · Stable Core v1  
**Сервис:** `elaya-stagecoach-web` (Render)  
**Ветка:** `develop`

---

## 1) Что сделано

- Поднят минимальный **портал StageCoach** (UI) + API (FastAPI).
- Включены сервисные эндпоинты:  
  - `GET /healthz` → `{"status":"ok"}`
  - `GET /api/status` → снапшот ядра
  - `POST /api/sync` → инкремент цикла + отметка времени
  - `POST /api/reflection` → приём заметки (UI → CORE)
  - `GET /api/timeline` → события ядра
- Смонтирован статик, подключён **theme.css** (тёмная тема).
- Добавлен **UI-дашборд**: кнопки *Синхронизировать*, *Обновить статус*, *Добавить заметку*, *Открыть таймлайн*.
- Введён **X-Guard-Key** (ключ из UI хранится в `localStorage` и уходит заголовком).

---

## 2) Проверка (ручные прогоны)

HTTP:
```bash
# здоровье
curl -s https://elaya-stagecoach-web.onrender.com/healthz

# статус
curl -s https://elaya-stagecoach-web.onrender.com/api/status | jq .

# синхронизация (пример через PowerShell/Invoke-RestMethod уже обкатан)
# ожидаем: cycle += 1, last_update -> ISO8601
