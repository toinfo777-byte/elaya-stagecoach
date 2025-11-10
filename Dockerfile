# Dockerfile (web)
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# полезные утилиты: sqlite3-cli для быстрой диагностики через Render Shell
RUN apt-get update && apt-get install -y --no-install-recommends \
      sqlite3 ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# зависимости
COPY requirements.txt .
RUN pip install -r requirements.txt

# код
COPY app ./app

# дефолтные env (в Render можно переопределить)
ENV ENV=staging \
    MODE=web \
    BOT_PROFILE=hq \
    PORT=10000 \
    BUILD_MARK=manual

# на всякий создаём точку монтирования для диска Render
RUN mkdir -p /data

# запуск FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]
