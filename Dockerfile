FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY app ./app

# Render задаёт PORT; локально по умолчанию будет 10000
CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}
