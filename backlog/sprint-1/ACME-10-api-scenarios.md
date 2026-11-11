# ACME-10 · First 9 eval cases from Acme Shield

| Owner | Size | Session | Depends on | Skills | Estimate / Actual |
| --- | --- | --- | --- | --- | --- |
| you | M | Sun Nov 15 | ACME-2 to ACME-6, ACME-8, ACME-9 | 1 API · 3 investigation · 6 Python | 2.5 h / __ |

## Context
The eval set is what P1's resume number rests on. These are its first 9 cases, recorded from
real exchanges with Acme Shield: no hand-written HTTP.

## Requirements
Using the scenario runner from ACME-9, write scenario functions that each produce a case
folder `evals/cases/<issue_type>_<nn>/` with the evidence files and a `label.yaml`:

| issue_type | clean | multi_file | noisy |
| --- | --- | --- | --- |
| api_key_invalid | test key on live, HAR only | bad scheme, HAR + server log | test key, plus favicon 404s and an analytics call |
| rate_limited | burst past 60/min, HAR only | burst, HAR + server log | burst with retries sent before `Retry-After`, plus noise |
| scim_user_conflict | 409 on a re-push, HAR only | HAR + server log | 409 among several successful 201s |

Each `label.yaml` follows the schema in the P1 guide (issue_type, classification, owner,
key_findings, variant, split, notes). Leave `split: dev` for now; the split is set in ACME-30.

## Acceptance criteria
- `python -m acme_shield.scenarios` writes all 9 folders, from scratch, the same way twice.
- A test (provided with ACME-9) loads every `label.yaml` and checks its values against the
  `diagx.models` enums.
- One generated HAR imports into Chrome DevTools (Network tab → import).

## Notes
Exact function signatures and the recorder's API land with ACME-9 (Claude's PR, by Saturday).
This ticket gets its final hint and test details then.

## Stretch, if time is left
Add `server_error_defect` ×3 and `account_billing_hold` ×3 now (they're due in ACME-30).
