FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app

WORKDIR /app

COPY requirements.txt .
RUN python -m pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY entrypoint.py ./entrypoint.py

ENV ENV=staging \
    MODE=worker \
    BUILD_MARK=manual

CMD ["python", "entrypoint.py"]
