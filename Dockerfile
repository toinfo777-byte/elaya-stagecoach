# Базовый образ
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Общий рабочий каталог проекта
WORKDIR /app

# Устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Кладём внутрь весь проект
COPY . .

# 🔹 Команда по умолчанию — запуск WEB (FastAPI)
#   Локально порт будет 8000, на Render — $PORT
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
