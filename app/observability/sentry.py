from __future__ import annotations
import os
import logging
import sentry_sdk

from .diag_status import mark_sentry_ok

def init_sentry(env: str, release: str) -> bool:
    dsn = os.getenv("SENTRY_DSN", "").strip()
    if not dsn:
        logging.info("Sentry DSN is empty — skip init.")
        return False

    sentry_sdk.init(
        dsn=dsn,
        environment=env,
        release=release,
        traces_sample_rate=0.0,  # без performance на этом этапе
        send_default_pii=False,
    )
    logging.info("Sentry initialized for env=%s, release=%s", env, release)
    return True

def capture_test_message() -> None:
    try:
        sentry_sdk.capture_message("✅ Sentry test message from Elaya bot")
        mark_sentry_ok()
    except Exception as e:
        logging.warning("Sentry test capture failed: %s", e)
