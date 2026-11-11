# ACME-8 · Evidence models

| Owner | Size | Session | Depends on | Skills | Estimate / Actual |
| --- | --- | --- | --- | --- | --- |
| you | S | Sun Nov 15 | — | 6 Python | 1 h / __ |

## Context
Every stage of diagx passes the same kinds of objects around: evidence files, facts pulled
out of them, and findings. Defining them once, with validation, means a typo in a label or a
naive timestamp fails loudly at the boundary instead of quietly skewing the eval.

## Requirements
Create `diagx/models.py` with:
- `StrEnum`s: `IssueType` (13 values, from the failure catalog), `Classification` (4),
  `Owner` (5), `Severity` (`low`, `medium`, `high`, in that order), `EvidenceKind` (`har`,
  `saml`, `jwt`, `log`, `webhook_log`, `tenant_config`).
- Pydantic models, all **frozen** (immutable):
  - `EvidenceFile(name, kind, raw: bytes, sha256)` with a classmethod
    `from_bytes(name, kind, raw)` that computes the SHA-256.
  - `HarRequestFact(index, started_at, method, url, status, request_id=None,
    headers_of_interest={}, form_params={}, error_body=None)`. `started_at` must be
    timezone-aware.
  - `Finding(id, code, severity, source, observed, expected, message)`. `id` must match
    `F<digits>`.
- Delete the temporary `[[tool.mypy.overrides]]` block for `tests.diagx.test_models` at the
  bottom of `pyproject.toml`.

## Acceptance criteria
`tests/diagx/test_models.py`: 7 tests, and `make check` green with the override removed.

## Out of scope
The other fact models (SAML, JWT, logs, webhook, tenant). Each arrives with its parser ticket.

## Learn first (10 min)
- **`StrEnum`** members are also strings, so `IssueType.RATE_LIMITED == "rate_limited"` is
  True. Labels loaded from YAML compare cleanly.
- **Pydantic v2** building blocks: `model_config = ConfigDict(frozen=True)`;
  `Field(pattern=r"...")` for regex validation; `AwareDatetime` as a type that rejects naive
  datetimes; `Field(default_factory=dict)` for mutable defaults.
- **Why frozen:** findings are evidence. If a later stage could edit one, the escalation
  report could cite something the parser never saw.

<details><summary>Hint 1 (direction)</summary>

A small base class with the frozen config, which the three models inherit, keeps it to one
line. `from_bytes` is three lines: hash, then `return cls(...)`.
</details>

## Explain-back (answer in the PR)
1. What does `frozen=True` protect against in this pipeline, specifically?
2. Why reject a naive `started_at`? Give the concrete bug it prevents when comparing a JWT's
   `exp` with the request time.
