# app/mw_sentry.py
from __future__ import annotations
import time, uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import sentry_sdk
from sentry_sdk import Hub

class SentryBreadcrumbs(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        rid = uuid.uuid4().hex[:8]
        with Hub.current:
            sentry_sdk.add_breadcrumb(
                category="http.request",
                message=f"{request.method} {request.url.path}",
                level="info",
                data={"rid": rid}
            )
        start = time.time()
        resp = await call_next(request)
        dur = round((time.time() - start) * 1000)
        sentry_sdk.add_breadcrumb(
            category="http.response",
            message=f"{resp.status_code} {request.url.path}",
            level="info",
            data={"rid": rid, "ms": dur}
        )
        return resp
