import os
import sys
import subprocess
import logging

MODE = os.getenv("MODE", "web").lower()
ENV = os.getenv("ENV", "staging")
PORT = int(os.getenv("PORT", "10000"))

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
log = logging.getLogger("entrypoint")

log.info("🚀 Starting Elaya container | MODE=%s | ENV=%s", MODE, ENV)

try:
    if MODE == "web":
        log.info("🌐 Launching Web server on port %s ...", PORT)
        # Стартуем uvicorn на объекте FastAPI "app" в модуле app.main
        subprocess.run(
            [sys.executable, "-m", "uvicorn", "app.main:app",
             "--host", "0.0.0.0", "--port", str(PORT)],
            check=True
        )

    elif MODE == "worker":
        log.info("🤖 Launching HQ Worker Bot (polling mode)...")
        # Внутри app.main есть __main__ со стартом poll’инга (run_app())
        subprocess.run([sys.executable, "-m", "app.main"], check=True)

    else:
        raise RuntimeError(f"Unknown MODE={MODE!r}")

except subprocess.CalledProcessError as e:
    log.error("Subprocess exited with error code %s", e.returncode)
    raise
