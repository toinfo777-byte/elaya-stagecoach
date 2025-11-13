from fastapi import FastAPI
from app.routes import api, ui, system   # ← ДОБАВИЛ system

app = FastAPI()

# --- РАУТЕРЫ ---
app.include_router(api.router)
app.include_router(system.router)   # ← ДОБАВИЛ system-router
app.include_router(ui.router)
