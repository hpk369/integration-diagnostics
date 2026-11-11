"""API-key authentication. Ticket ACME-2 (yours).

Contract
--------
Clients send `Authorization: Bearer <key>`. This service runs as the *live* environment.

| Situation                                   | Status | error.code                 |
| ------------------------------------------- | ------ | -------------------------- |
| No Authorization header                     | 401    | invalid_api_key            |
| Scheme isn't Bearer (`Token x`, bare key)   | 401    | invalid_api_key            |
| Bearer with an unknown key                  | 401    | invalid_api_key            |
| Known key, but its env is `test`            | 401    | key_environment_mismatch   |
| Known live key                              | —      | returns AuthContext        |

Every 401 also sends `WWW-Authenticate: Bearer error="invalid_token"`.
On success, set `request.state.tenant_id` so the access log records the tenant.

Tenants live on `request.app.state.tenants` (a TenantStore).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated

from fastapi import Header, Request

from acme_shield.tenants import Tenant

SERVICE_ENV = "live"
WWW_AUTHENTICATE = 'Bearer error="invalid_token"'


@dataclass(frozen=True)
class AuthContext:
    tenant: Tenant
    api_key: str


def require_api_key(
    request: Request,
    authorization: Annotated[str | None, Header()] = None,
) -> AuthContext:
    """FastAPI dependency: authenticate the caller or raise ApiError(401, ...)."""
    raise NotImplementedError("ACME-2: implement require_api_key")
