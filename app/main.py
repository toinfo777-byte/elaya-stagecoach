-from app.routers import (
+from app.routers import (
     entrypoints,
     help,
     cmd_aliases,
     onboarding,
     system,
     minicasting,
     leader,
     training,
     progress,
     privacy,
     settings as settings_mod,
     extended,
     casting,
     apply,
     faq,
     devops_sync,
     panic,
-    diag,  # health/diag/status_json
+    diag,  # health/diag/status_json
+    hq,    # HQ summary
 )
@@
     smoke_modules = [
         "app.routers.entrypoints",
         "app.routers.help",
         "app.routers.cmd_aliases",
         "app.routers.onboarding",
         "app.routers.system",
         "app.routers.minicasting",
         "app.routers.leader",
         "app.routers.training",
         "app.routers.progress",
         "app.routers.privacy",
         "app.routers.settings",
         "app.routers.extended",
         "app.routers.casting",
         "app.routers.apply",
         "app.routers.faq",
         "app.routers.devops_sync",
+        "app.routers.hq",
         "app.routers.panic",
         "app.routers.diag",
     ]
@@
     dp.include_router(devops_sync.router);   log.info("✅ router loaded: devops_sync")
+    dp.include_router(hq.router);            log.info("✅ router loaded: hq")
     dp.include_router(panic.router);         log.info("✅ router loaded: panic (near last)")
     dp.include_router(diag.router);          log.info("✅ router loaded: diag (last)")
