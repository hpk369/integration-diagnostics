"""Acceptance tests for ACME-8: the shared evidence models in diagx/models.py.

When you start ACME-8, delete the `pytestmark` line below.
"""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

pytestmark = pytest.mark.skip(reason="ACME-8 not started")


def test_issue_types_match_the_failure_catalog() -> None:
    from diagx.models import IssueType

    assert {t.value for t in IssueType} == {
        "saml_clock_skew",
        "saml_audience_mismatch",
        "saml_signing_cert_rotated",
        "saml_nameid_mismatch",
        "oidc_redirect_uri_mismatch",
        "jwt_expired_or_wrong_claims",
        "api_key_invalid",
        "rate_limited",
        "webhook_signature_invalid",
        "scim_user_conflict",
        "server_error_defect",
        "account_billing_hold",
        "insufficient_evidence",
    }


def test_classification_owner_and_severity_values() -> None:
    from diagx.models import Classification, Owner, Severity

    assert {c.value for c in Classification} == {
        "configuration",
        "expected_behavior",
        "product_defect",
        "specialist_owned",
    }
    assert {o.value for o in Owner} == {
        "customer_admin",
        "customer_dev",
        "engineering",
        "billing",
        "support",
    }
    assert [s.value for s in Severity] == ["low", "medium", "high"]


def test_enums_compare_equal_to_their_string_values() -> None:
    # Labels come from YAML as plain strings; comparisons must just work.
    from diagx.models import IssueType

    assert IssueType.RATE_LIMITED == "rate_limited"


def test_evidence_file_from_bytes_computes_sha256() -> None:
    from diagx.models import EvidenceFile, EvidenceKind

    raw = b'{"log": {"entries": []}}'
    ev = EvidenceFile.from_bytes("customer.har", EvidenceKind.HAR, raw)
    assert ev.sha256 == hashlib.sha256(raw).hexdigest()
    assert ev.name == "customer.har"
    assert ev.kind == "har"


def test_har_request_fact_requires_timezone_aware_time() -> None:
    from diagx.models import HarRequestFact

    fact = HarRequestFact(
        index=3,
        started_at=datetime(2026, 11, 15, 9, 30, tzinfo=UTC),
        method="GET",
        url="https://api.acmeshield.example/v1/scans",
        status=429,
    )
    assert fact.request_id is None
    assert fact.headers_of_interest == {}
    with pytest.raises(ValidationError):
        HarRequestFact(
            index=3,
            started_at=datetime(2026, 11, 15, 9, 30),  # naive: no timezone
            method="GET",
            url="https://api.acmeshield.example/v1/scans",
            status=429,
        )


def test_finding_ids_look_like_f_numbers() -> None:
    from diagx.models import Finding, Severity

    ok = Finding(
        id="F3",
        code="SAML_CERT_FINGERPRINT_MISMATCH",
        severity=Severity.HIGH,
        source="customer.har#entries[14]",
        observed="ab12…",
        expected="cd34…",
        message="Signing cert fingerprint doesn't match the tenant config.",
    )
    assert ok.id == "F3"
    for bad in ("3", "f3", "F", "F3a"):
        with pytest.raises(ValidationError):
            Finding(**{**ok.model_dump(), "id": bad})


def test_models_are_immutable() -> None:
    # Facts and findings are evidence: nothing downstream should edit them.
    from diagx.models import Finding, Severity

    f = Finding(
        id="F1",
        code="X",
        severity=Severity.LOW,
        source="s",
        observed="o",
        expected="e",
        message="m",
    )
    with pytest.raises(ValidationError):
        f.id = "F2"
