from __future__ import annotations
import os
from dataclasses import dataclass

def _get(name: str, default: str | None = None) -> str:
    v = os.getenv(name, default)
    if v is None:
        raise RuntimeError(f"ENV {name} is required")
    return v

@dataclass(frozen=True)
class Settings:
    token: str = _get("TG_BOT_TOKEN")
    env: str = os.getenv("ENV", "staging")
    mode: str = os.getenv("MODE", "worker")
    build_mark: str = os.getenv("BUILD_MARK", "manual")
    # Render envs (если есть — красиво покажем в /hq)
    render_git_commit: str = os.getenv("RENDER_GIT_COMMIT", "")
    render_service: str = os.getenv("RENDER_SERVICE_NAME", "")
    render_instance: str = os.getenv("RENDER_INSTANCE_ID", "")
    render_region: str = os.getenv("RENDER_REGION", "")

settings = Settings()
