FROM python:3.12-slim

# Базовые настройки Python и pip
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Тулза для healthcheck (curl) — в slim-образе её нет
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Зависимости
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Код приложения
COPY app ./app

# Healthcheck: Render дёргает контейнер — проверяем наш /healthz
HEALTHCHECK --interval=30s --timeout=3s --start-period=15s --retries=3 \
  CMD curl -fsS "http://127.0.0.1:${PORT:-10000}/healthz" || exit 1

# Запуск uvicorn; Render передаёт $PORT
CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}
