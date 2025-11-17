# app/main.py
from fastapi import FastAPI
from app.routes import api, ui, system  # веб-якоря

app = FastAPI()

# --- РОУТЕРЫ веб-ядра ---
app.include_router(api.router)
app.include_router(system.router)
app.include_router(ui.router)
