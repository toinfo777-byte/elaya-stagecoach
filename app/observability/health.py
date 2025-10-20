# app/observability/health.py
from __future__ import annotations
import logging

def boot_health(*, env: str, release: str) -> None:
    logging.getLogger("health").info("Health boot: env=%s release=%s", env, release)
