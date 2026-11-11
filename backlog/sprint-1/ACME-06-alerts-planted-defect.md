# ACME-6 · Alerts endpoint with a planted defect

| Owner | Size | Session | Depends on | Skills | Estimate / Actual |
| --- | --- | --- | --- | --- | --- |
| you | XS | Sat Nov 14 | ACME-2 | 3 investigation · 6 Python | 30 m / __ |

## Context
diagx has to tell **product defects** apart from customer mistakes. To have defect evidence,
Acme Shield needs a real bug: `GET /v1/alerts` crashes when `org_id` is missing, instead of
returning a 400. You're writing the bug on purpose, and marking it clearly.

## Requirements
- New router `acme_shield/routes/alerts.py` with `GET /v1/alerts`, protected by
  `Authenticated`. Include it in `create_app`.
- With `?org_id=<id>`: `200`, body `{"data": [...]}`, at least one alert, each with `id`,
  `org_id` (the one requested), `domain` and `severity`.
- Without `org_id`: the code reads it as `params["org_id"]` from
  `dict(request.query_params)`, so it raises `KeyError`. Mark that line with
  `# PLANTED DEFECT (ACME-6): ...`.
- Don't catch the error. The scaffold's middleware turns it into a 500 envelope and logs the
  stack trace. That log line is the evidence.

## Acceptance criteria
`tests/acme_shield/test_alerts.py`: 3 tests.

## Out of scope
Fixing the bug. Real alert data.

<details><summary>Hint 1 (direction)</summary>

Copy the shape of `routes/scans.py`. The route takes `request: Request` and `auth: Authenticated`.
Build two or three fake alerts in a list comprehension using the `org_id` you read.
</details>

## Try it by hand
`make run`, call it with and without `org_id`, and read the server log line for the 500.
Find the `request_id` in both the response and the log.

## Explain-back (answer in the PR)
1. What in the evidence (response, log line, repeatability) tells you this is a product
   defect and not a customer misconfiguration?
2. Write the "Expected behavior / Actual behavior" lines you'd put in the escalation.
