"""Request IDs and JSON access logs.

Every request gets an ID (`req_` + 16 hex chars). It goes into `request.state.request_id`,
the `X-Request-Id` response header and one JSON log line, so evidence from the customer
side (a HAR) and the server side (logs) can be joined on it.

Log line fields: ts, level, request_id, tenant_id, method, path, status, duration_ms,
error_code, and `stack` on unhandled errors.
"""

from __future__ import annotations

import json
import logging
import secrets
import time
import traceback
from datetime import UTC, datetime

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from acme_shield.errors import error_body

REQUEST_ID_HEADER = "X-Request-Id"
access_log = logging.getLogger("acme_shield.access")


def new_request_id() -> str:
    return f"req_{secrets.token_hex(8)}"


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        request.state.request_id = new_request_id()
        started = time.perf_counter()
        stack: str | None = None
        try:
            response = await call_next(request)
        except (
            Exception
        ) as exc:  # anything a route didn't handle becomes a 500 envelope
            stack = "".join(traceback.format_exception(exc))
            request.state.error_code = "internal_error"
            response = JSONResponse(
                status_code=500,
                content=error_body(
                    "internal_error", "Something went wrong.", request.state.request_id
                ),
            )
        response.headers[REQUEST_ID_HEADER] = request.state.request_id
        record = {
            "ts": datetime.now(UTC).isoformat(timespec="milliseconds"),
            "level": "error" if response.status_code >= 500 else "info",
            "request_id": request.state.request_id,
            "tenant_id": getattr(request.state, "tenant_id", None),
            "method": request.method,
            "path": request.url.path,
            "status": response.status_code,
            "duration_ms": round((time.perf_counter() - started) * 1000, 2),
            "error_code": getattr(request.state, "error_code", None),
        }
        if stack:
            record["stack"] = stack
        access_log.log(
            logging.ERROR if response.status_code >= 500 else logging.INFO,
            json.dumps(record),
        )
        return response
