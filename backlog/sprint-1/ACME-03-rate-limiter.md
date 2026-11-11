# ACME-3 · Per-key rate limiter

| Owner | Size | Session | Depends on | Skills | Estimate / Actual |
| --- | --- | --- | --- | --- | --- |
| you | XS | Fri Nov 13 | ACME-2 (for the two HTTP tests) | 1 API troubleshooting · 6 Python | 30 m / __ |

## Context
One enterprise tenant's nightly sync bursts `/v1/scans` hard enough to slow it for everyone.
Product wants 60 requests per minute per key, and a 429 that tells clients exactly when to
retry. Later, diagx will spot customers who ignore `Retry-After`. That only works if this
header is right.

## Requirements
Implement `FixedWindowRateLimiter.check(key)` in `acme_shield/ratelimit.py`. The contract
is in the module docstring:
- Windows are 60 s, aligned to the clock (they start at multiples of 60).
- Each call counts one request for that key in the current window.
- `allowed` stays True for the first `limit` requests in a window.
- `remaining` = requests left after this one, never below 0.
- `reset_after_s` = seconds until the window ends, rounded **up**, at least 1.

The HTTP wiring (headers and the 429) is already in `acme_shield/deps.py`. Read it, but
you don't need to change it.

## Acceptance criteria
`tests/acme_shield/test_ratelimit.py`: 9 tests (7 unit tests, 2 HTTP tests).

## Out of scope
Sliding windows, token buckets, Redis or any shared store, per-tenant limits, cleaning up old
windows. That last one comes back as an explain-back question.

## Learn first (5 min)
- **Window math.** With `now = 1_000_035.5`, the window number is `int(now // 60)`. The window
  ends at `(window + 1) * 60`. So the time left is `end - now`, rounded up with `math.ceil`.
- **Why the clock is injected:** the tests pass a fake clock and call `clock.advance(59)`
  instead of sleeping for a minute. Use `self._clock()`, never `time.time()`, inside `check`.
- **A dict can be keyed by a tuple:** `counts[(key, window)] = n`.

<details><summary>Hint 1 (direction)</summary>

`check` needs four steps: read the clock once; work out the window; increment that key's
count for that window; build the decision from the count. Every field of the decision comes
from `count`, `limit`, `now` and `window`.
</details>

## Explain-back (answer in the PR)
1. Your counter dict never deletes old windows. When would that become a problem in
   production, and what's one way to fix it?
2. Acme Shield runs on three servers behind a load balancer. What happens to this limiter,
   and what would you tell a customer who says "I only sent 40 requests"?
