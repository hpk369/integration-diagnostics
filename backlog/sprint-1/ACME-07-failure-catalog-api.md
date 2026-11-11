# ACME-7 · Failure catalog: the API entries

| Owner | Size | Session | Depends on | Skills | Estimate / Actual |
| --- | --- | --- | --- | --- | --- |
| you | S | Sat Nov 14 | ACME-2 to ACME-6 | 4 technical communication | 1 h / __ |

## Context
The failure catalog is the label spec for the eval set and the first draft of the KB articles
P2 will search. You just built the behavior behind five of them, so write them while it's fresh.

## Requirements
In `docs/failure-catalog.md`, write entries for:
`api_key_invalid`, `rate_limited`, `scim_user_conflict`, `server_error_defect`,
`account_billing_hold`. Use the entry template at the top of the file and tick the table.

## Acceptance criteria
- Each entry has all six fields.
- Each "Evidence signature" names concrete things a parser would see: status, header,
  `error.code`, log field.
- Each "Customer-facing sentence" passes the test: would a customer admin understand it with
  no other context?
- No code changes. CI still needs a changelog entry (type `docs`).

## Explain-back
Pick one entry and explain it to me twice: once as you would to an engineer, once as you
would to the customer's manager.
