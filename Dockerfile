FROM python:3.12-slim

# базовые оптимизации
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app

WORKDIR /app

# быстрее и чище установка зависимостей
COPY requirements.txt .
RUN python -m pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# само приложение
COPY app ./app

# дефолты (в Render они переопределяются в Environment)
ENV ENV=staging \
    MODE=worker \
    BUILD_MARK=manual

# единая точка входа — внутри app.main вы уже ветвитесь по MODE
CMD ["python", "-m", "app.main"]
