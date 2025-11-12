from fastapi import APIRouter
from app.core.state import StateStore

router = APIRouter()

@router.get("/status")
async def api_status():
    core = StateStore.get().get_state()
    return {
        "ok": True,
        "core": core.snapshot(),
    }

@router.post("/sync")
async def api_sync():
    core = StateStore.get().sync(source="ui")
    return {
        "ok": True,
        "message": "synced",
        "core": core.snapshot(),
    }
