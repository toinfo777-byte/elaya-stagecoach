# Dockerfile
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# системные библиотеки (по минимуму)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

# сначала зависимости — лучше кэшируются
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# затем код
COPY . .

# запуск бота
CMD ["python", "-m", "app.main"]
