"""Acceptance tests for ACME-2: API-key authentication.

When you start ACME-2, delete the `pytestmark` line below. Don't change the tests to
make them pass; if you think a test is wrong, say so in the PR.
"""

from __future__ import annotations

import httpx
import pytest
from fastapi.testclient import TestClient

from .conftest import LIVE_KEY, TEST_KEY, access_records, bearer

pytestmark = pytest.mark.skip(reason="ACME-2 not started")

CHALLENGE = 'Bearer error="invalid_token"'


def assert_401(resp: httpx.Response, code: str) -> None:
    assert resp.status_code == 401
    assert resp.headers["WWW-Authenticate"] == CHALLENGE
    body = resp.json()["error"]
    assert body["code"] == code
    assert body["request_id"] == resp.headers["X-Request-Id"]
    assert body["message"]  # a human-readable sentence, not empty


def test_valid_live_key_is_accepted(client: TestClient) -> None:
    resp = client.get("/v1/scans", headers=bearer(LIVE_KEY))
    assert resp.status_code == 200
    assert resp.json()["data"]


def test_missing_header_is_rejected(client: TestClient) -> None:
    assert_401(client.get("/v1/scans"), "invalid_api_key")


@pytest.mark.parametrize(
    "header",
    [
        f"Token {LIVE_KEY}",  # wrong scheme
        LIVE_KEY,  # bare key, no scheme
        "Bearer",  # scheme with no key
        "Bearer ",  # scheme with an empty key
    ],
)
def test_malformed_header_is_rejected(client: TestClient, header: str) -> None:
    assert_401(
        client.get("/v1/scans", headers={"Authorization": header}), "invalid_api_key"
    )


def test_scheme_is_case_insensitive(client: TestClient) -> None:
    # RFC 7235: the auth scheme name is case-insensitive.
    resp = client.get("/v1/scans", headers={"Authorization": f"bearer {LIVE_KEY}"})
    assert resp.status_code == 200


def test_unknown_key_is_rejected(client: TestClient) -> None:
    assert_401(
        client.get(
            "/v1/scans", headers=bearer("acme_live_ffffffffffffffffffffffffffffffff")
        ),
        "invalid_api_key",
    )


def test_test_key_against_live_is_an_environment_mismatch(client: TestClient) -> None:
    assert_401(
        client.get("/v1/scans", headers=bearer(TEST_KEY)), "key_environment_mismatch"
    )


def test_tenant_is_recorded_in_access_log(
    client: TestClient, caplog: pytest.LogCaptureFixture
) -> None:
    client.get("/v1/scans", headers=bearer(LIVE_KEY))
    assert access_records(caplog)[-1]["tenant_id"] == "fernhollow"


def test_failed_auth_logs_the_error_code(
    client: TestClient, caplog: pytest.LogCaptureFixture
) -> None:
    client.get("/v1/scans", headers=bearer(TEST_KEY))
    record = access_records(caplog)[-1]
    assert record["status"] == 401
    assert record["error_code"] == "key_environment_mismatch"
