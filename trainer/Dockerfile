# Dockerfile — контейнер для elaya-trainer-worker

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# --- базовый рабочий каталог ---
WORKDIR /app

# зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# весь проект внутрь
COPY . .

# --- запуск тренера (aiogram) ---
CMD ["python", "-m", "app.main"]
