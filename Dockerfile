# syntax=docker/dockerfile:1
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

# Базовые системные пакеты (минимум; можно убрать build-essential, если не нужен)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 1) Ставим зависимости (кэш слоёв)
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# 2) Копируем приложение
COPY . .

# 3) Даём права на запуск entrypoint
RUN chmod +x docker/entrypoint.sh

# Render прокинет PORT для web; выставляем дефолт на всякий случай
ENV PORT=8000
EXPOSE 8000

# Универсальная точка входа — см. docker/entrypoint.sh
CMD ["docker/entrypoint.sh"]
