from __future__ import annotations

import importlib
import logging
import pkgutil
from typing import List

from aiogram import Router
import app.routers as routers_pkg  # пакет с твоими модулями-роутерами

log = logging.getLogger("import")

def import_and_collect_routers() -> List[Router]:
    """Динамически импортирует все модули из app.routers и собирает переменную `router`."""
    collected: List[Router] = []

    for mod_info in pkgutil.iter_modules(routers_pkg.__path__):
        mod_name = mod_info.name
        fqmn = f"{routers_pkg.__name__}.{mod_name}"
        try:
            module = importlib.import_module(fqmn)
        except Exception as e:
            log.debug("Import miss %s: %s", fqmn, e)
            continue

        # Ищем объект роутера в модуле
        router_obj = None
        for attr in ("router", "rt", "router_v3"):
            r = getattr(module, attr, None)
            if isinstance(r, Router):
                router_obj = r
                break

        # Иногда роутер лежит в подмодуле ...<name>.router
        if router_obj is None:
            try:
                sub = importlib.import_module(f"{fqmn}.router")
                r = getattr(sub, "router", None)
                if isinstance(r, Router):
                    router_obj = r
            except Exception as e:
                log.debug("Import miss %s.router: %s", fqmn, e)

        if isinstance(router_obj, Router):
            collected.append(router_obj)
        else:
            log.debug("No Router found in %s", fqmn)

    return collected
