# ACME-4 · Suspended accounts get 403

| Owner | Size | Session | Depends on | Skills | Estimate / Actual |
| --- | --- | --- | --- | --- | --- |
| you | XS | Sat Nov 14 | ACME-2, ACME-3 | 1 API troubleshooting · 3 escalation | 30 m / __ |

## Context
When an invoice fails, Billing suspends the tenant. Right now a suspended tenant's calls still
work, or, worse, return 429 when they retry. That sends their developers debugging rate limits
instead of calling Billing. This is the "specialist-owned" case in the failure catalog.

## Requirements
- New module `acme_shield/billing.py` with a dependency `require_active_account` that depends on
  `require_api_key`.
- A tenant with `billing_status == "suspended"` gets `ApiError(403, "account_suspended", ...)`.
  The message must mention billing, so the customer knows who can fix it.
- Re-wire `acme_shield/deps.py` so the chain is **auth → billing → rate limit**.

## Acceptance criteria
`tests/acme_shield/test_billing.py`: 4 tests.

## Out of scope
Grace periods, read-only mode, reactivation.

## Learn first (5 min)
- **Dependency chains:** a dependency can depend on another one,
  `auth: Annotated[AuthContext, Depends(require_api_key)]`. FastAPI runs them in order and
  caches each one per request, so auth runs once even if two dependencies need it.
- In `deps.py`, `enforce_rate_limit` currently depends on `require_api_key`. Change what it
  depends on, and the order changes.

<details><summary>Hint 1 (direction)</summary>

`require_active_account` is about five lines: take the `AuthContext`, check the tenant's
billing status, raise or return the same context. Then one import and one `Depends(...)`
change in `deps.py`.
</details>

## Explain-back (answer in the PR)
1. Why must billing run before the rate limiter? Describe what the customer sees if it doesn't.
2. Why 403 here and not 401?
