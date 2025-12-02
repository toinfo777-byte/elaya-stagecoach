# Dockerfile — контейнер для elaya-trainer-worker

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# --- базовый рабочий каталог ---
WORKDIR /app

# зависимости (общие для проекта)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем ТОЛЬКО папку тренера внутрь контейнера
COPY trainer ./trainer

# Переходим в каталог тренера
WORKDIR /app/trainer

# --- запуск тренера (aiogram) ---
CMD ["python", "-m", "app.main"]
