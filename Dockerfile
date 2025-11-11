FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

# Render автоматически добавляет PORT, используем его
CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}
