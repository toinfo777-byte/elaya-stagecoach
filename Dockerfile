# syntax=docker/dockerfile:1.7
FROM python:3.10-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VIRTUALENVS_CREATE=0 \
    PORT=10000

WORKDIR /app

# Системные зависимости (опционально расширяйте по мере надобности)
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    curl bash ca-certificates tzdata gcc \
 && rm -rf /var/lib/apt/lists/*

# Зависимости Python
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Исходники приложения
COPY . /app

# entrypoint
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 10000

# MODE управляет запуском (web / worker). LOG_LEVEL — в нижнем регистре: info|warning|error|critical|debug|trace
ENV MODE=web \
    LOG_LEVEL=info

# Не используем shell-обёртки, чтобы сигналы доходили до процесса
CMD ["/entrypoint.sh"]
