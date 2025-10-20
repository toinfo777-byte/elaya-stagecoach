# app/build.py
from __future__ import annotations
import os
from dataclasses import dataclass

@dataclass(frozen=True)
class BuildInfo:
    build_mark: str
    git_sha: str
    image_tag: str
    env: str

def _env(name: str, default: str = "unknown") -> str:
    v = (os.getenv(name) or default).strip()
    return v or default

BUILD = BuildInfo(
    build_mark=_env("BUILD_MARK", "local"),
    git_sha=_env("SHORT_SHA", "local"),
    image_tag=_env("IMAGE_TAG", "ghcr.io/unknown/elaya-stagecoach:develop"),
    env=_env("ENV", "develop"),
)
