import os
import sys
import subprocess
import logging

MODE = os.getenv("MODE", "worker").lower()
ENV = os.getenv("ENV", "develop")
PORT = os.getenv("PORT", "8000")

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("entrypoint")

log.info(f"🚀 Starting Elaya container | MODE={MODE} | ENV={ENV}")

try:
    if MODE == "worker":
        # режим бота (polling)
        log.info("🔁 Launching HQ Worker Bot (polling mode)...")
        subprocess.run([sys.executable, "-m", "app.main"], check=True)

    elif MODE == "web":
        # режим вебхуков / web API
        log.info(f"🌐 Launching Web server on port {PORT} ...")
        subprocess.run([
            "uvicorn", "app.main:fastapi",
            "--host", "0.0.0.0",
            "--port", PORT,
            "--log-level", "info"
        ], check=True)

    else:
        log.error(f"❌ Unknown MODE '{MODE}'. Expected 'worker' or 'web'.")
        sys.exit(1)

except subprocess.CalledProcessError as e:
    log.error(f"💥 Subprocess exited with error code {e.returncode}")
    sys.exit(e.returncode)
except Exception as e:
    log.exception(f"⚠️ Unexpected exception: {e}")
    sys.exit(1)
