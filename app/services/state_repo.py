from typing import Optional, Tuple
from app.storage import db

def save_last_scene(user_id: int, scene: Optional[str] = None, reflect: Optional[str] = None):
    db.save_scene(user_id, scene, reflect)

def get_last_scene(user_id: int) -> Tuple[Optional[str], Optional[str], Optional[int]]:
    return db.get_scene(user_id)
