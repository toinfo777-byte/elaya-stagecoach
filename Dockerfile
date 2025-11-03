FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app ./app
COPY entrypoint.py ./entrypoint.py

# Значения можно переопределить в Render → Environment
ENV ENV=staging \
    MODE=web \
    PORT=10000 \
    BUILD_MARK=manual

# 🟢 Ключевая правка:
# Запускаем entrypoint только если RUN_CONTEXT=render
CMD ["bash", "-c", "if [ \"$RUN_CONTEXT\" = 'render' ]; then python -m entrypoint; else echo 'Skipping bot run (build context detected)'; fi"]
