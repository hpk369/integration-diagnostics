# ACME-5 · SCIM user provisioning with 409 conflicts

| Owner | Size | Session | Depends on | Skills | Estimate / Actual |
| --- | --- | --- | --- | --- | --- |
| you | S | Sat Nov 14 | ACME-2 | 2 SSO and identity · 1 API | 1.5 h / __ |

## Context
Customers connect their identity provider (Okta, Entra ID) to Acme Shield with SCIM, so new
employees get accounts automatically. A classic ticket: "provisioning fails for some users."
Usually an admin created those users by hand before turning SCIM on. The IdP's `POST` then
collides with the existing user and gets a 409. Acme Shield needs to produce that 409
exactly as the SCIM spec describes, because that's what admins paste into tickets.

## Requirements
- New router `acme_shield/routes/scim.py` with `POST /scim/v2/Users`, protected by the
  `Authenticated` dependency. Include it in `create_app`.
- An in-memory directory per tenant on `app.state`, created in `create_app`.
- Success: `201`, content type `application/scim+json`, body with `schemas`, server-assigned
  `id`, `userName`, `active`, and `meta.resourceType == "User"`.
- `userName` already exists in that tenant (**case-insensitive**): `409` with the SCIM error
  body (`schemas`, `status` as the string `"409"`, `scimType: "uniqueness"`, `detail` naming
  the user), and `request.state.error_code = "scim_uniqueness"`.
- Missing or empty `userName`: `400`, `scimType: "invalidValue"`, error code
  `scim_invalid_value`.

## Acceptance criteria
`tests/acme_shield/test_scim.py`: 6 tests.

## Out of scope
GET, PATCH, DELETE, filtering, groups, persistence.

## Learn first (10 min)
- **SCIM** (RFC 7643/7644) is a standard REST API for user provisioning. The IdP is the client;
  Acme Shield is the server. `POST /Users` creates a user.
- **SCIM errors have their own format:** they don't use Acme Shield's error envelope. Note
  the `status` field is a **string**. Interviewers like that detail.
- **Why not a pydantic body model here?** If you declare a model with a required `userName`,
  FastAPI returns its own 422 before your code runs, and the SCIM test expects a SCIM-shaped
  400. Read the raw JSON with `await request.json()` (so the route is `async def`) and validate
  it yourself.
- Return a `JSONResponse(status_code=..., content=..., media_type="application/scim+json")`.

<details><summary>Hint 1 (direction)</summary>

Shape the directory as `{tenant_id: {lowercased_user_name: user_dict}}`. One small helper,
`scim_error(status, scim_type, detail)`, builds both error responses. The route reads the body,
validates `userName`, finds the tenant's users, checks for the lowercased name, then stores and
returns the new user.
</details>

## Try it by hand
Run the same `curl -X POST` twice and compare the two responses. The second is what an Okta
admin sees in their provisioning log.

## Explain-back (answer in the PR)
1. An admin says "SCIM fails for 12 of our 400 users." What do you suspect, and what do you
   ask them to check?
2. Why is the uniqueness check case-insensitive, and what would go wrong if it weren't?
