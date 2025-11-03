FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY entrypoint.py ./entrypoint.py

# Значения можно переопределить в Render → Environment
ENV ENV=staging \
    MODE=web \
    PORT=10000 \
    RUN_CONTEXT=render \
    BUILD_MARK=manual

EXPOSE 10000

# Всегда запускаем entrypoint: он сам решит, что поднять (web или worker) по MODE
CMD ["python", "-m", "entrypoint"]
