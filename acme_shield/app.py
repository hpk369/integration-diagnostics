"""Acme Shield app factory.

Run locally:  uv run uvicorn acme_shield.app:app --reload
Tests build their own app with create_app(clock=...) so time is controllable.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from pathlib import Path

from fastapi import FastAPI

from acme_shield.errors import ApiError, api_error_handler
from acme_shield.middleware import RequestContextMiddleware
from acme_shield.ratelimit import FixedWindowRateLimiter
from acme_shield.routes import health, scans
from acme_shield.tenants import DEFAULT_TENANTS_PATH, TenantStore

RATE_LIMIT_PER_MINUTE = 60


def create_app(
    tenants_path: Path = DEFAULT_TENANTS_PATH,
    clock: Callable[[], float] = time.time,
    rate_limit_per_minute: int = RATE_LIMIT_PER_MINUTE,
) -> FastAPI:
    app = FastAPI(title="Acme Shield (fictional)", version="0.1.0")
    app.state.tenants = TenantStore.from_yaml(tenants_path)
    app.state.rate_limiter = FixedWindowRateLimiter(rate_limit_per_minute, clock=clock)

    app.add_middleware(RequestContextMiddleware)
    app.add_exception_handler(ApiError, api_error_handler)

    app.include_router(health.router)
    app.include_router(scans.router)
    # ACME-5 and ACME-6 add their routers here.
    return app


logging.basicConfig(level=logging.INFO, format="%(message)s")
app = create_app()
