# -------- base image
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_NO_CACHE_DIR=off

WORKDIR /app

# Системные зависимости для asyncpg и др.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc curl \
 && rm -rf /var/lib/apt/lists/*

# -------- deps
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# -------- app
COPY . .

# Включим entrypoint и дадим право на исполнение
RUN chmod +x docker/entrypoint.sh

# Render пробрасывает порт через переменные, но на Starter стабильнее явно держать 10000
EXPOSE 10000

# ВНИМАНИЕ: запуск всегда через entrypoint — он сам решает web/worker
CMD ["docker/entrypoint.sh"]
