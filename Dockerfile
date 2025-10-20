# ---- base ----
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# === метаданные билда (передаются build-args из Actions)
ARG BUILD_MARK=local
ARG SHORT_SHA=local
ARG IMAGE_TAG=ghcr.io/unknown/elaya-stagecoach:develop
ENV BUILD_MARK=${BUILD_MARK} \
    SHORT_SHA=${SHORT_SHA} \
    IMAGE_TAG=${IMAGE_TAG}

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
ENV PYTHONPATH=/app

# === запись метаданных в финальный .env (читается ботом при старте)
RUN echo "BUILD_MARK=${BUILD_MARK}" >> /app/.env \
 && echo "SHORT_SHA=${SHORT_SHA}" >> /app/.env \
 && echo "IMAGE_TAG=${IMAGE_TAG}" >> /app/.env \
 && echo "ENV=develop" >> /app/.env

CMD ["python", "-m", "app.main"]
