"""Pattern 5 — The runtime environment is part of the reliability surface.

A tool that works perfectly in code can still silently fail to run because
of a PATH resolution difference between how the reference environment was
configured and how the process actually got started. The visible symptom is
a generic "command not found" buried among log lines — easy to misread as
"the target wasn't vulnerable" instead of "the tool never ran".

The fix is not a runbook note telling operators to remember to export the
right variable. It's making the process itself guarantee its own execution
environment, regardless of how it was launched.
"""

from __future__ import annotations

import asyncio
import os
import shutil
from typing import Sequence

# Common install locations for security tooling across platforms. Extend
# this list for your own environment — the point is that the list lives in
# code, not in a launch script someone has to remember to source correctly.
_DEFENSIVE_PATH_DIRS = (
    "/opt/homebrew/bin",
    "/opt/homebrew/sbin",
    "/usr/local/bin",
    os.path.expanduser("~/.local/bin"),
)


def _env_with_guaranteed_path() -> dict[str, str]:
    env = os.environ.copy()
    existing = env.get("PATH", "").split(os.pathsep)
    for directory in _DEFENSIVE_PATH_DIRS:
        if directory not in existing:
            env["PATH"] = directory + os.pathsep + env.get("PATH", "")
    return env


async def run_tool(cmd: Sequence[str], timeout: int = 60) -> str:
    """Every external-binary call in the system should go through this,
    never through a bare asyncio.create_subprocess_exec with an inherited,
    unverified environment."""
    env = _env_with_guaranteed_path()

    resolved = shutil.which(cmd[0], path=env.get("PATH"))
    if resolved is None:
        # Fail loud and specific — never let this collapse into a
        # generic "target not vulnerable" result downstream.
        return f"[tool not found: {cmd[0]} — checked {env.get('PATH')}]"

    try:
        proc = await asyncio.create_subprocess_exec(
            resolved, *cmd[1:],
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
        )
        out, _ = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        return out.decode(errors="replace")
    except asyncio.TimeoutError:
        return f"[timeout after {timeout}s: {' '.join(cmd)}]"


if __name__ == "__main__":
    async def _demo() -> None:
        result = await run_tool(["echo", "tool executed with a guaranteed PATH"])
        print(result.strip())

    asyncio.run(_demo())
