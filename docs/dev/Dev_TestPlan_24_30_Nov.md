# Dev Test Plan · 24–30 Nov 2025

Цель недели: убедиться, что связка  
**CLI → Core → Trainer → UI → HQ**  
работает стабильно после введения GUARD, sync и расширения цикла.

---

## 0. Окружение

**Core (web-core):**
- ветка: `develop`
- переменные:
  - `GUARD_KEY` (включаем со вторника)
  - `CORE_VERSION = "0.5.1"`

**CLI (elaya-cli):**
- установка: `pip install -e .`
- переменные:
  - `ELAYA_CORE_URL`
  - `ELAYA_GUARD_KEY` (для тестов с GUARD)

**Trainer-bot:**
- ветка: `develop`
- переменные:
  - `TRAINER_CORE_URL`
  - `TRAINER_GUARD_KEY`

---

## 1. GUARD · защита мутирующих запросов

### 1.1. CLI без ключа (до включения GUARD)

**Шаги:**
1. Убедиться, что в окружении **нет** `ELAYA_GUARD_KEY`.
2. В ядре `GUARD_KEY` либо не задан, либо защита ещё не включена логически.
3. Выполнить:
   - `elaya3 intro`
   - `elaya3 reflect`
   - `elaya3 transition`
   - `elaya3 event`
4. Проверить `/api/timeline`.

**Ожидается:**
- все команды проходят (`2xx` на стороне ядра),
- события появляются в таймлайне,
- ошибок авторизации нет.

---

### 1.2. Включение GUARD на ядре

**Шаги:**
1. Задать переменную окружения `GUARD_KEY` на web-core.
2. Перезапустить сервис ядра.
3. Не задавать пока `ELAYA_GUARD_KEY`/`TRAINER_GUARD_KEY`.

**Ожидается:**
- GET-запросы (`/api/status`, `/api/healthz`, `/api/cycle/state`, `/api/timeline`) продолжают работать.
- Все POST-запросы без ключа начинают возвращать `401 invalid guard key`.

(Фактические проверки — в следующих сценариях.)

---

### 1.3. CLI без ключа при включённом GUARD

**Шаги:**
1. Убедиться, что `GUARD_KEY` задан на ядре.
2. В окружении **нет** `ELAYA_GUARD_KEY`.
3. Выполнить:
   - `elaya3 intro`
   - `elaya3 reflect`
   - `elaya3 transition`
   - `elaya3 event`.

**Ожидается:**
- каждая команда падает с понятной ошибкой:
  - на стороне ядра → HTTP `401`
  - в CLI → сообщение вида  
    `⚠ Ошибка запроса ... 401 Client Error: ...`
- GET-команда `elaya3 status` продолжает работать.

---

### 1.4. CLI с корректным ключом

**Шаги:**
1. В окружении ядра: `GUARD_KEY=some-secret`.
2. В окружении CLI: `ELAYA_GUARD_KEY=some-secret`.
3. Выполнить:
   - `elaya3 intro`
   - `elaya3 reflect`
   - `elaya3 transition`
   - `elaya3 event`.
4. Проверить `/api/timeline`.

**Ожидается:**
- команды снова проходят (`2xx`),
- события пишутся в таймлайн,
- в логах больше нет `401`,
- GET-команды (status, cycle) работают как раньше.

---

### 1.5. Trainer с неверным ключом

**Шаги:**
1. В ядре: `GUARD_KEY=some-secret`.
2. В окружении тренера: `TRAINER_GUARD_KEY=wrong-secret`.
3. Вызвать в тренер-боте:
   - сцену `intro`,
   - сцену `reflect`,
   - сцену `transition`.

**Ожидается:**
- попытки отправить события в ядро заканчиваются `401`,
- тренер логирует ошибку (без падения процесса),
- в `/api/timeline` нет новых событий от источника `trainer`.

---

### 1.6. Trainer с корректным ключом

**Шаги:**
1. В ядре: `GUARD_KEY=some-secret`.
2. В тренере: `TRAINER_GUARD_KEY=some-secret`.
3. Снова пройти:
   - `intro`,
   - `reflect`,
   - `transition`.

**Ожидается:**
- события от тренера появляются в `/api/timeline` с `source = "trainer"`,
- ошибок `401` нет,
- CLI и тренер сосуществуют без конфликтов.

---

## 2. Sync Protocol · /api/sync + elaya3 sync

### 2.1. Ответ ядра /api/sync

**Шаги:**
1. Вызвать через браузер или curl: `GET /api/sync`.
2. Проверить структуру ответа.

**Ожидается (примерная структура):**
```json
{
  "ok": true,
  "core_version": "0.5.1",
  "cli_min_version": "0.5.0",
  "cycle": { ... },
  "events_count": <int>,
  "server_time": "<iso8601>",
  "status": "ok"
}
