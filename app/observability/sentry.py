# app/observability/sentry.py
from __future__ import annotations
import os
import sentry_sdk

def init_sentry(*, env: str, release: str, send_test: bool = False) -> None:
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        environment=env or "develop",
        release=release or "local",
        enable_tracing=False,  # включишь при необходимости
        traces_sample_rate=float(os.getenv("SENTRY_TRACES", "0.0") or 0.0),
    )
    if send_test:
        with sentry_sdk.push_scope() as scope:
            scope.set_tag("startup_probe", "1")
            sentry_sdk.capture_message("Elaya bot started (startup probe)")
