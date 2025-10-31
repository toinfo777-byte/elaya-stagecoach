FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app ./app

# переменные можно переопределять в Render
ENV ENV=staging \
    MODE=worker \
    BUILD_MARK=manual

CMD ["python", "-m", "app.main"]
