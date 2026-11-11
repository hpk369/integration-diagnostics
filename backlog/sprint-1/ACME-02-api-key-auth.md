# ACME-2 · API-key authentication

| Owner | Size | Session | Depends on | Skills | Estimate / Actual |
| --- | --- | --- | --- | --- | --- |
| you | XS | Wed Nov 11 | ACME-1 merged | 1 API troubleshooting · 6 Python | 30 m / __ |

## Context
Acme Shield's API is open to anyone right now. Customers call it with an API key, and
support sees a steady stream of "401 but my key is right" tickets. Usually the customer is
using a **test** key against the **live** API, or sending the key with the wrong scheme.
The error has to tell them which, so they can fix it without opening a ticket.

## Requirements
Implement `require_api_key` in `acme_shield/auth.py`. The contract table is in the
module docstring. In short:
- Read `Authorization`. It must be `Bearer <key>`. The scheme is case-insensitive.
- Missing header, wrong scheme, empty key or unknown key → `ApiError(401, "invalid_api_key", ...)`
- Known key whose env is `test` → `ApiError(401, "key_environment_mismatch", ...)`
- Every 401 sends the header `WWW-Authenticate: Bearer error="invalid_token"`
- On success, set `request.state.tenant_id` and return `AuthContext(tenant, api_key)`

## Acceptance criteria
`tests/acme_shield/test_auth.py`: 11 tests. Delete its `pytestmark` line first.

## Out of scope
Key hashing, key rotation, scopes and permissions, OAuth.

## Learn first (5 min)
- **A FastAPI dependency** is a function FastAPI calls before your route runs. Its
  parameters can be the `Request`, a header (`authorization: Annotated[str | None, Header()]`
  reads the `Authorization` header), or another dependency. If it raises, the route never
  runs. Here, `ApiError` becomes the JSON error via the handler in `errors.py`.
- **Where the tenants are:** `request.app.state.tenants` is a `TenantStore`.
  `lookup_key(key)` returns `(tenant, key_record)` or `None`.
- **Why 401, not 403:** 401 means "I don't know who you are", and it must say how to
  authenticate (`WWW-Authenticate`). 403 means "I know who you are, and you can't do this."
  You'll write a 403 in ACME-4.

<details><summary>Hint 1 (direction)</summary>

Handle the cases in the same order as the table, and return early from each. Splitting the
header once on the first space gives you the scheme and the key. Look at what
`str.partition(" ")` returns for `"Bearer"`, `"Bearer "` and `"Bearer abc"`.
A small helper that builds the 401 `ApiError` with the header saves repeating it.
</details>

## Try it by hand
`make run`, then:
```bash
curl -i http://127.0.0.1:8000/v1/scans -H "Authorization: Bearer acme_test_00000000000000000000000000000f02"
```
Read the status, the `WWW-Authenticate` header, the body and `X-Request-Id`. That's what a
customer would paste into a ticket.

## Explain-back (answer in the PR)
1. Why is a test key on the live API a different `error.code` from an unknown key? How does
   that change what support says to the customer?
2. Why does setting `request.state.tenant_id` matter to someone reading the logs at 2 a.m.?
