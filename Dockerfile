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

# Старт через uvicorn (webhook режим)
CMD ["uvicorn", "app.entrypoint_web:app", "--host", "0.0.0.0", "--port", "10000"]
