# app/observability/sentry.py
from __future__ import annotations
import logging
import os
from typing import Optional

import sentry_sdk

SENTRY_OK: bool = False  # публичный флажок для /diag


def setup_sentry(*, dsn: str, env: str, release: str) -> bool:
    global SENTRY_OK
    if not dsn:
        SENTRY_OK = False
        return False

    sentry_sdk.init(
        dsn=dsn,
        environment=env,
        release=release or "local",
        traces_sample_rate=float(os.getenv("SENTRY_TRACES", "0.0") or 0.0),
    )
    SENTRY_OK = True
    return True


def capture_test_message(msg: str = "Sentry test message from Elaya bot") -> None:
    try:
        sentry_sdk.capture_message(msg)
    except Exception as e:
        logging.warning("Sentry test message failed: %s", e)
