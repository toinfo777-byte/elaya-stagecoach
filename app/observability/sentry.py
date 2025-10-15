# app/observability/sentry.py
from __future__ import annotations
from typing import Optional
import sentry_sdk

def init_sentry(*, dsn: Optional[str], env: str = "prod", release: Optional[str] = None) -> None:
    if not dsn:
        print("SENTRY: DSN not provided ⚠️")
        return
    sentry_sdk.init(
        dsn=dsn,
        environment=env,
        release=release,
        traces_sample_rate=0.0,
        send_default_pii=False,
    )
    print(f"SENTRY: initialized ✅ env={env} release={release}")

def capture_test_message() -> None:
    try:
        sentry_sdk.capture_message("✅ Sentry test message from Elaya bot")
        print("SENTRY: test message sent ✅")
    except Exception as e:
        print(f"SENTRY: test message failed ❌ {e}")
