"""Acceptance tests for ACME-6: GET /v1/alerts, with a planted product defect.

When you start ACME-6, delete the `pytestmark` line below. Needs ACME-2.
The 500 is deliberate: it's the "product defect" evidence diagx must later recognise.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from .conftest import LIVE_KEY, access_records, bearer

pytestmark = pytest.mark.skip(reason="ACME-6 not started")


def test_alerts_for_an_org(client: TestClient) -> None:
    resp = client.get(
        "/v1/alerts", params={"org_id": "fernhollow-hq"}, headers=bearer(LIVE_KEY)
    )
    assert resp.status_code == 200
    alerts = resp.json()["data"]
    assert len(alerts) >= 1
    assert all(a["org_id"] == "fernhollow-hq" for a in alerts)
    assert {"id", "org_id", "domain", "severity"} <= alerts[0].keys()


def test_planted_defect_missing_org_id_is_a_500(
    client: TestClient, caplog: pytest.LogCaptureFixture
) -> None:
    resp = client.get("/v1/alerts", headers=bearer(LIVE_KEY))
    assert resp.status_code == 500
    assert resp.json()["error"]["code"] == "internal_error"
    record = access_records(caplog)[-1]
    assert record["level"] == "error"
    assert record["tenant_id"] == "fernhollow"
    assert "KeyError" in record["stack"]
    assert "org_id" in record["stack"]


def test_defect_is_reproducible(client: TestClient) -> None:
    # Same request shape, same failure: that's what makes it escalatable.
    statuses = {
        client.get("/v1/alerts", headers=bearer(LIVE_KEY)).status_code for _ in range(3)
    }
    assert statuses == {500}
