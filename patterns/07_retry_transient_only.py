"""Pattern 7 — Retry the transient failure, accept the definitive one.

An audit of a real codebase found the same fragility repeated at more than
thirty call sites: any exception on a single request was treated as a
definitive miss. The fix is not "always retry" — retrying a genuine timeout
against a slow target wastes the phase's time budget without improving
recall. The fix is classifying the failure first.
"""

from __future__ import annotations

import asyncio
import random
from dataclasses import dataclass
from enum import Enum, auto


class Outcome(Enum):
    SUCCESS = auto()
    TRANSIENT = auto()   # connection error, 5xx, 429 rate-limit
    DEFINITIVE = auto()  # genuine timeout, 4xx, or any conclusive response


@dataclass
class RequestResult:
    outcome: Outcome
    attempts: int


async def request_with_bounded_retry(
    do_request,
    max_attempts: int = 3,
    backoff_seconds: float = 0.2,
) -> RequestResult:
    """`do_request` is an async callable returning an Outcome. Only
    TRANSIENT failures consume a retry; DEFINITIVE ones — including a real
    timeout against a slow target — are accepted immediately, so a slow
    target never eats a phase's whole time budget by being retried."""
    for attempt in range(1, max_attempts + 1):
        outcome = await do_request()
        if outcome is not Outcome.TRANSIENT:
            return RequestResult(outcome, attempt)
        if attempt < max_attempts:
            await asyncio.sleep(backoff_seconds * attempt)
    return RequestResult(Outcome.TRANSIENT, max_attempts)


if __name__ == "__main__":
    async def _demo() -> None:
        # A flaky endpoint: fails transiently twice, then succeeds.
        calls = {"n": 0}

        async def flaky_then_ok() -> Outcome:
            calls["n"] += 1
            return Outcome.SUCCESS if calls["n"] >= 3 else Outcome.TRANSIENT

        result = await request_with_bounded_retry(flaky_then_ok)
        print(f"flaky endpoint: {result.outcome.name} after {result.attempts} attempt(s)")

        # A genuinely slow target: every call times out for real. Retrying
        # this never helps — it should be accepted on the first attempt.
        async def genuinely_slow() -> Outcome:
            calls["n"] += 1
            return Outcome.DEFINITIVE

        result = await request_with_bounded_retry(genuinely_slow)
        print(f"slow target:    {result.outcome.name} after {result.attempts} attempt(s) "
              f"(no wasted retries on real latency)")

    asyncio.run(_demo())
