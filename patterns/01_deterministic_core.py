"""Pattern 1 — Deterministic core vs. LLM-discretionary periphery.

The naive design lets the agent decide, on every turn, which capability to
call. Measured against a real capability set, less than a third of them ran
with any guarantee. This pattern shows the fix: capabilities that must always
run are pulled out of the agent's discretion entirely and executed as a
deterministic sweep, in parallel, before the agent gets a turn. The agent is
left only with capabilities where judgment genuinely adds value.

This is illustrative scaffolding, not a real scanner. No target, tool, or
client name from the original system is reproduced here.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Awaitable, Callable


class Tier(Enum):
    CORE = auto()          # always runs, every execution, no exceptions
    DISCRETIONARY = auto()  # the agent may or may not choose to call it


@dataclass
class Capability:
    name: str
    tier: Tier
    run: Callable[[str], Awaitable[dict]]


@dataclass
class Orchestrator:
    capabilities: list[Capability] = field(default_factory=list)

    def register(self, name: str, tier: Tier, fn: Callable[[str], Awaitable[dict]]) -> None:
        self.capabilities.append(Capability(name, tier, fn))

    async def run_core_sweep(self, target: str) -> dict[str, dict]:
        """Runs every CORE capability unconditionally, in parallel.
        Coverage here never depends on model judgment."""
        core = [c for c in self.capabilities if c.tier is Tier.CORE]
        results = await asyncio.gather(*(c.run(target) for c in core))
        return {c.name: r for c, r in zip(core, results)}

    def discretionary_names(self) -> list[str]:
        """These are offered to the agent as tools it may call. Coverage
        here is a judgment call, by design — never route something that
        must always run through this list."""
        return [c.name for c in self.capabilities if c.tier is Tier.DISCRETIONARY]


# --- Example wiring -----------------------------------------------------

async def _check_missing_security_headers(target: str) -> dict:
    return {"finding": "missing-headers", "target": target, "confirmed": True}


async def _check_injection_surface(target: str) -> dict:
    return {"finding": "reflected-param", "target": target, "confirmed": True}


async def _speculative_chain_exploit(target: str) -> dict:
    # The kind of capability where an LLM's judgment about *whether* to
    # chain two findings together adds real value — a legitimate candidate
    # for the discretionary tier.
    return {"finding": "chained-exploit-hypothesis", "target": target, "confirmed": False}


async def main() -> None:
    orch = Orchestrator()
    orch.register("missing_headers", Tier.CORE, _check_missing_security_headers)
    orch.register("injection_surface", Tier.CORE, _check_injection_surface)
    orch.register("speculative_chain", Tier.DISCRETIONARY, _speculative_chain_exploit)

    core_results = await orch.run_core_sweep("example.test")
    print("Guaranteed this run:", list(core_results))
    print("Left to agent judgment:", orch.discretionary_names())


if __name__ == "__main__":
    asyncio.run(main())
