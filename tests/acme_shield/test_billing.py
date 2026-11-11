"""Acceptance tests for ACME-4: suspended accounts get 403 account_suspended.

When you start ACME-4, delete the `pytestmark` line below. Needs ACME-2 and ACME-3.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from acme_shield.app import create_app

from .conftest import LIVE_KEY, SUSPENDED_KEY, FakeClock, access_records, bearer

pytestmark = pytest.mark.skip(reason="ACME-4 not started")


def test_suspended_tenant_gets_403(client: TestClient) -> None:
    resp = client.get("/v1/scans", headers=bearer(SUSPENDED_KEY))
    assert resp.status_code == 403
    error = resp.json()["error"]
    assert error["code"] == "account_suspended"
    assert "billing" in error["message"].lower()  # tell the customer who can fix it


def test_active_tenant_is_unaffected(client: TestClient) -> None:
    assert client.get("/v1/scans", headers=bearer(LIVE_KEY)).status_code == 200


def test_billing_is_checked_before_the_rate_limit(clock: FakeClock) -> None:
    # A suspended tenant over its limit must still see 403, not 429:
    # 429 would send them debugging retries instead of calling Billing.
    client = TestClient(create_app(clock=clock, rate_limit_per_minute=1))
    for _ in range(3):
        assert client.get("/v1/scans", headers=bearer(SUSPENDED_KEY)).status_code == 403


def test_suspension_is_logged(
    client: TestClient, caplog: pytest.LogCaptureFixture
) -> None:
    client.get("/v1/scans", headers=bearer(SUSPENDED_KEY))
    record = access_records(caplog)[-1]
    assert record["tenant_id"] == "relaypoint"
    assert record["error_code"] == "account_suspended"
