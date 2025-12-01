# Dockerfile — контейнер для elaya-trainer-bot

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

# --- переходим в папку тренера ---
WORKDIR /app/trainer

# точка входа тренера (как ты запускаешь локально)
CMD ["python", "-m", "app.main"]
