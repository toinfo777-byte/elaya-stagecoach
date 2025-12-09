# Dockerfile — контейнер для elaya-stagecoach-web

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# --- базовый рабочий каталог ---
WORKDIR /app

# зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# весь проект внутрь
COPY . .

# Порт: по умолчанию 10000, но если Render задаст PORT, возьмём его
ENV PORT=10000
EXPOSE 10000

# --- HEALTHCHECK: стучимся в /api/healthz на текущем порту ---
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD python - << 'EOF'
import os, sys, http.client

port = int(os.environ.get("PORT", "10000"))

try:
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=2)
    conn.request("GET", "/api/healthz")
    resp = conn.getresponse()
    sys.exit(0 if resp.status == 200 else 1)
except Exception:
    sys.exit(1)
EOF

# --- запуск FastAPI ядра через uvicorn ---
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
