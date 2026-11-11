"""One error shape for every Acme Shield endpoint (except SCIM, which has its own).

    {"error": {"code": "invalid_api_key", "message": "...", "request_id": "req_..."}}

A fixed shape matters to support: one grep finds every failure, and the request_id
links a customer's screenshot to the server log line.
"""

from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse


class ApiError(Exception):
    """Raise this from a route or dependency to return a structured error."""

    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.headers = headers or {}


def error_body(
    code: str, message: str, request_id: str | None
) -> dict[str, dict[str, str | None]]:
    return {"error": {"code": code, "message": message, "request_id": request_id}}


async def api_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Registered on the app for ApiError. Also records the code for the access log."""
    assert isinstance(exc, ApiError)
    request.state.error_code = exc.code
    request_id = getattr(request.state, "request_id", None)
    return JSONResponse(
        status_code=exc.status_code,
        content=error_body(exc.code, exc.message, request_id),
        headers=exc.headers,
    )
