FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app ./app

ENV ENV=staging \
    MODE=web \
    PORT=10000 \
    BUILD_MARK=manual

EXPOSE 10000

# 🟢 Запускаем uvicorn только если RUN_CONTEXT=render
CMD ["bash", "-c", "if [ \"$RUN_CONTEXT\" = 'render' ]; then uvicorn app.main:app --host 0.0.0.0 --port $PORT; else echo 'Skipping web run (build context detected)'; fi"]
