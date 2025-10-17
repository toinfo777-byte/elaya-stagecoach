# app/observability/__init__.py
import logging
import sentry_sdk

def setup_observability(env: str, release: str, send_test: bool = True):
    try:
        dsn = os.getenv("SENTRY_DSN")
        if not dsn:
            logging.warning("⚠️ SENTRY_DSN not set — skipping Sentry init")
            return
        sentry_sdk.init(dsn=dsn, environment=env, release=release)
        logging.info("✅ Sentry initialized (%s, %s)", env, release)
        if send_test:
            sentry_sdk.capture_message("Sentry test message from Elaya bot")
    except Exception as e:
        logging.warning("⚠️ Sentry init failed: %s", e)
