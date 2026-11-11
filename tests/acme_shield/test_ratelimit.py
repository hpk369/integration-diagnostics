"""Acceptance tests for ACME-3: per-key fixed-window rate limiting.

When you start ACME-3, delete the `pytestmark` line below. The HTTP tests at the bottom
also need ACME-2 (auth) to be merged.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from acme_shield.app import create_app
from acme_shield.ratelimit import FixedWindowRateLimiter

from .conftest import LIVE_KEY, OTHER_LIVE_KEY, FakeClock, bearer

pytestmark = pytest.mark.skip(reason="ACME-3 not started")

# ---------- unit tests: the limiter on its own ----------


def test_first_request_is_allowed(clock: FakeClock) -> None:
    d = FixedWindowRateLimiter(60, clock=clock).check("k")
    assert d.allowed
    assert d.limit == 60
    assert d.remaining == 59


def test_request_over_the_limit_is_denied(clock: FakeClock) -> None:
    limiter = FixedWindowRateLimiter(60, clock=clock)
    decisions = [limiter.check("k") for _ in range(61)]
    assert all(d.allowed for d in decisions[:60])
    assert decisions[59].remaining == 0
    assert not decisions[60].allowed
    assert decisions[60].remaining == 0


def test_reset_after_rounds_up_to_whole_seconds(clock: FakeClock) -> None:
    limiter = FixedWindowRateLimiter(60, clock=clock)
    clock.advance(15.5)  # 44.5 s left in the window
    assert limiter.check("k").reset_after_s == 45


def test_reset_after_is_never_zero(clock: FakeClock) -> None:
    limiter = FixedWindowRateLimiter(60, clock=clock)
    clock.advance(59.9)
    assert limiter.check("k").reset_after_s == 1


def test_counter_resets_in_the_next_window(clock: FakeClock) -> None:
    limiter = FixedWindowRateLimiter(2, clock=clock)
    limiter.check("k")
    limiter.check("k")
    assert not limiter.check("k").allowed
    clock.advance(60)
    d = limiter.check("k")
    assert d.allowed
    assert d.remaining == 1


def test_window_boundary_is_aligned_to_the_clock(clock: FakeClock) -> None:
    # Fixed windows start at multiples of 60, not at each key's first request.
    limiter = FixedWindowRateLimiter(1, clock=clock)
    clock.advance(59)
    assert limiter.check("k").allowed
    clock.advance(1)  # new window begins now
    assert limiter.check("k").allowed


def test_keys_do_not_share_a_counter(clock: FakeClock) -> None:
    limiter = FixedWindowRateLimiter(1, clock=clock)
    assert limiter.check("a").allowed
    assert not limiter.check("a").allowed
    assert limiter.check("b").allowed


# ---------- HTTP tests: needs ACME-2 merged ----------


def test_http_429_carries_retry_after_and_rate_limit_headers(clock: FakeClock) -> None:
    client = TestClient(create_app(clock=clock, rate_limit_per_minute=2))
    clock.advance(10)
    ok = client.get("/v1/scans", headers=bearer(LIVE_KEY))
    assert ok.status_code == 200
    assert ok.headers["X-RateLimit-Limit"] == "2"
    assert ok.headers["X-RateLimit-Remaining"] == "1"

    client.get("/v1/scans", headers=bearer(LIVE_KEY))
    denied = client.get("/v1/scans", headers=bearer(LIVE_KEY))
    assert denied.status_code == 429
    assert denied.json()["error"]["code"] == "rate_limited"
    assert denied.headers["Retry-After"] == "50"
    assert denied.headers["X-RateLimit-Remaining"] == "0"


def test_http_other_tenant_is_not_affected(clock: FakeClock) -> None:
    client = TestClient(create_app(clock=clock, rate_limit_per_minute=1))
    client.get("/v1/scans", headers=bearer(LIVE_KEY))
    assert client.get("/v1/scans", headers=bearer(LIVE_KEY)).status_code == 429
    assert client.get("/v1/scans", headers=bearer(OTHER_LIVE_KEY)).status_code == 200
