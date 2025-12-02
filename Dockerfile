# Dockerfile — контейнер для elaya-stagecoach-web

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

# --- запуск FastAPI ядра через uvicorn ---
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]
