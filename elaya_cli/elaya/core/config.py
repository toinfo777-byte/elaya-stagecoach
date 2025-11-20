from __future__ import annotations

from pathlib import Path
import os

# Базовая информация об агенте
APP_NAME = "Elaya CLI Agent"
APP_VERSION = "0.4.1"

# Корень проекта: elaya-stagecoach/
PROJECT_ROOT = Path(__file__).resolve().parents[3]

# Стандартные директории внутри проекта
DOCS_DIR = PROJECT_ROOT / "docs"
APP_DIR = PROJECT_ROOT / "app"

# Настройки подключения к web-core
# Пример (потом): ELAYA_CORE_URL="https://elaya-core.onrender.com"
CORE_URL: str = os.getenv("ELAYA_CORE_URL", "").strip().rstrip("/")
CORE_GUARD_KEY: str = os.getenv("ELAYA_CORE_GUARD_KEY", "").strip()

# Таймауты для сетевых запросов (в секундах)
CORE_TIMEOUT: float = float(os.getenv("ELAYA_CORE_TIMEOUT", "2.5") or 2.5)
