"""Acceptance tests for ACME-5: SCIM user provisioning with 409 conflicts.

When you start ACME-5, delete the `pytestmark` line below. Needs ACME-2.
SCIM errors use the SCIM error format from RFC 7644 section 3.12, not our usual envelope.
"""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient

from .conftest import LIVE_KEY, OTHER_LIVE_KEY, access_records, bearer

pytestmark = pytest.mark.skip(reason="ACME-5 not started")

USER_SCHEMA = "urn:ietf:params:scim:schemas:core:2.0:User"
ERROR_SCHEMA = "urn:ietf:params:scim:api:messages:2.0:Error"
SCIM_JSON = "application/scim+json"


def new_user(user_name: str) -> dict[str, Any]:
    return {"schemas": [USER_SCHEMA], "userName": user_name, "active": True}


def post_user(client: TestClient, key: str, user_name: str) -> Any:
    return client.post(
        "/scim/v2/Users",
        json=new_user(user_name),
        headers={**bearer(key), "Content-Type": SCIM_JSON},
    )


def test_create_user_returns_201_scim_resource(client: TestClient) -> None:
    resp = post_user(client, LIVE_KEY, "maria.chen@fernhollow.example")
    assert resp.status_code == 201
    assert resp.headers["Content-Type"].startswith(SCIM_JSON)
    body = resp.json()
    assert body["schemas"] == [USER_SCHEMA]
    assert body["userName"] == "maria.chen@fernhollow.example"
    assert body["id"]  # server-assigned
    assert body["meta"]["resourceType"] == "User"


def test_duplicate_user_name_is_a_409_uniqueness_error(client: TestClient) -> None:
    post_user(client, LIVE_KEY, "maria.chen@fernhollow.example")
    resp = post_user(client, LIVE_KEY, "maria.chen@fernhollow.example")
    assert resp.status_code == 409
    assert resp.headers["Content-Type"].startswith(SCIM_JSON)
    body = resp.json()
    assert body["schemas"] == [ERROR_SCHEMA]
    assert body["status"] == "409"  # a string in SCIM, not a number
    assert body["scimType"] == "uniqueness"
    assert "maria.chen@fernhollow.example" in body["detail"]


def test_user_name_uniqueness_ignores_case(client: TestClient) -> None:
    # SCIM core schema: userName is not case-exact (RFC 7643 section 4.1.1).
    post_user(client, LIVE_KEY, "maria.chen@fernhollow.example")
    assert (
        post_user(client, LIVE_KEY, "Maria.Chen@Fernhollow.example").status_code == 409
    )


def test_tenants_have_separate_directories(client: TestClient) -> None:
    post_user(client, LIVE_KEY, "sam.lee@shared.example")
    assert (
        post_user(client, OTHER_LIVE_KEY, "sam.lee@shared.example").status_code == 201
    )


def test_missing_user_name_is_a_400_invalid_value(client: TestClient) -> None:
    resp = client.post(
        "/scim/v2/Users",
        json={"schemas": [USER_SCHEMA]},
        headers={**bearer(LIVE_KEY), "Content-Type": SCIM_JSON},
    )
    assert resp.status_code == 400
    body = resp.json()
    assert body["status"] == "400"
    assert body["scimType"] == "invalidValue"


def test_conflict_is_logged(
    client: TestClient, caplog: pytest.LogCaptureFixture
) -> None:
    post_user(client, LIVE_KEY, "maria.chen@fernhollow.example")
    post_user(client, LIVE_KEY, "maria.chen@fernhollow.example")
    record = access_records(caplog)[-1]
    assert record["status"] == 409
    assert record["error_code"] == "scim_uniqueness"
