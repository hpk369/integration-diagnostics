"""Dependency chains shared by routes.

Order matters and is part of the contract support relies on:
    authenticate → (ACME-4: billing check) → rate limit
A suspended tenant should get 403 even when it's also over its rate limit.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Request, Response

from acme_shield.auth import AuthContext, require_api_key
from acme_shield.errors import ApiError
from acme_shield.ratelimit import FixedWindowRateLimiter


def enforce_rate_limit(
    request: Request,
    response: Response,
    auth: Annotated[AuthContext, Depends(require_api_key)],
) -> AuthContext:
    limiter: FixedWindowRateLimiter = request.app.state.rate_limiter
    decision = limiter.check(auth.api_key)
    headers = {
        "X-RateLimit-Limit": str(decision.limit),
        "X-RateLimit-Remaining": str(decision.remaining),
        "X-RateLimit-Reset": str(decision.reset_after_s),
    }
    if not decision.allowed:
        raise ApiError(
            429,
            "rate_limited",
            f"Rate limit of {decision.limit} requests per minute exceeded.",
            headers={**headers, "Retry-After": str(decision.reset_after_s)},
        )
    response.headers.update(headers)
    return auth


# Use this on customer-facing API routes.
Authenticated = Annotated[AuthContext, Depends(enforce_rate_limit)]
