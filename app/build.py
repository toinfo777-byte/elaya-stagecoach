# app/build.py
from __future__ import annotations
import os
from dataclasses import dataclass

def _get(k: str, default: str = "local") -> str:
    v = (os.getenv(k) or "").strip()
    return v if v else default

@dataclass(frozen=True)
class BuildInfo:
    build_mark: str
    git_sha: str
    image_tag: str
    env: str

    @property
    def sha7(self) -> str:
        return (self.git_sha or "")[:7]

def _read() -> BuildInfo:
    return BuildInfo(
        build_mark=_get("BUILD_MARK"),
        git_sha=_get("SHORT_SHA", _get("GITHUB_SHA", "local")),
        image_tag=_get("IMAGE_TAG", "ghcr.io/unknown/elaya-stagecoach:develop"),
        env=_get("ENV", "develop"),
    )

BUILD = _read()
