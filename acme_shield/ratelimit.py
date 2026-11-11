"""Per-key rate limiting. Ticket ACME-3 (yours).

Contract
--------
Fixed window of 60 seconds per API key. Windows start at multiples of 60 on the clock
(for example 120.0 to 179.999...), so every key's window rolls over at the same moment.

`check(key)` counts the request and returns a decision:
- allowed:        True while the key has made at most `limit` requests in this window
- limit:          the configured limit
- remaining:      requests left in this window after this one (never below 0)
- reset_after_s:  whole seconds until the window resets, rounded up, at least 1

The clock is injected so tests can move time without sleeping.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass

WINDOW_SECONDS = 60


@dataclass(frozen=True)
class RateLimitDecision:
    allowed: bool
    limit: int
    remaining: int
    reset_after_s: int


class FixedWindowRateLimiter:
    def __init__(self, limit: int, clock: Callable[[], float] = time.time) -> None:
        self.limit = limit
        self._clock = clock
        # ACME-3: add the state you need to count requests per key per window.

    def check(self, key: str) -> RateLimitDecision:
        raise NotImplementedError("ACME-3: implement FixedWindowRateLimiter.check")
