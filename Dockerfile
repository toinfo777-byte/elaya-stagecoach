# Dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# (необязательно, но удобно, чтобы в Render Web Shell был cli sqlite3)
RUN apt-get update && apt-get install -y --no-install-recommends sqlite3 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app ./app
COPY entrypoint.py ./entrypoint.py

# Значения можно переопределить в Render → Environment
ENV ENV=staging \
    MODE=web \
    PORT=10000 \
    BUILD_MARK=manual

# Стартуем FastAPI-приложение из app.main:app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]
