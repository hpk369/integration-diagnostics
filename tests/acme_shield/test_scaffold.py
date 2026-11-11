"""Tests for the scaffold itself (ACME-1). These run from day one."""

from __future__ import annotations

import re

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from acme_shield.errors import ApiError
from acme_shield.tenants import TenantStore

from .conftest import access_records

REQUEST_ID = re.compile(r"^req_[0-9a-f]{16}$")


def test_healthz_ok_with_request_id(client: TestClient) -> None:
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
    assert REQUEST_ID.match(resp.headers["X-Request-Id"])


def test_access_log_line_has_the_documented_fields(
    client: TestClient, caplog: pytest.LogCaptureFixture
) -> None:
    resp = client.get("/healthz")
    [record] = access_records(caplog)
    assert record["request_id"] == resp.headers["X-Request-Id"]
    assert record["method"] == "GET"
    assert record["path"] == "/healthz"
    assert record["status"] == 200
    assert record["level"] == "info"
    assert {"ts", "tenant_id", "duration_ms", "error_code"} <= record.keys()


def test_api_error_becomes_the_standard_envelope(
    app: FastAPI, caplog: pytest.LogCaptureFixture
) -> None:
    @app.get("/boom-handled")
    def boom_handled() -> None:
        raise ApiError(418, "teapot", "I am a teapot.", headers={"X-Extra": "1"})

    resp = TestClient(app).get("/boom-handled")
    assert resp.status_code == 418
    assert resp.headers["X-Extra"] == "1"
    body = resp.json()
    assert body == {
        "error": {
            "code": "teapot",
            "message": "I am a teapot.",
            "request_id": resp.headers["X-Request-Id"],
        }
    }
    assert access_records(caplog)[-1]["error_code"] == "teapot"


def test_unhandled_exception_is_a_500_envelope_with_stack_in_log(
    app: FastAPI, caplog: pytest.LogCaptureFixture
) -> None:
    @app.get("/boom-unhandled")
    def boom_unhandled() -> None:
        raise KeyError("org_id")

    resp = TestClient(app).get("/boom-unhandled")
    assert resp.status_code == 500
    assert resp.json()["error"]["code"] == "internal_error"
    record = access_records(caplog)[-1]
    assert record["level"] == "error"
    assert "KeyError" in record["stack"]


def test_tenant_store_lookups() -> None:
    store = TenantStore.from_yaml()
    found = store.lookup_key("acme_live_00000000000000000000000000000f01")
    assert found is not None
    tenant, key = found
    assert tenant.tenant_id == "fernhollow"
    assert key.env == "live"
    assert store.lookup_key("acme_live_nope") is None
    relaypoint = store.get("relaypoint")
    assert relaypoint is not None
    assert relaypoint.billing_status == "suspended"
