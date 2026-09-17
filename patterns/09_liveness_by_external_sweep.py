"""Pattern 9 — A process that freezes cannot report that it froze.

A scan's own heartbeat mechanism runs INSIDE the same loop that can freeze —
so when the loop hangs waiting on a target that never responds, the
heartbeat hangs with it, and "status: running" never changes. No purely
internal mechanism can detect this, by definition. It takes an external
observer measuring elapsed time, not the task's own claim of being alive.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass
class TaskState:
    status: str = "running"
    last_heartbeat: float = field(default_factory=time.monotonic)

    def beat(self) -> None:
        self.last_heartbeat = time.monotonic()


def external_liveness_sweep(task: TaskState, stale_after_seconds: float) -> bool:
    """Runs on its own independent timer, never inside the task's loop.
    Returns True if it marked the task failed."""
    if task.status != "running":
        return False
    idle = time.monotonic() - task.last_heartbeat
    if idle > stale_after_seconds:
        task.status = "failed"
        print(f"[sweep] no heartbeat for {idle:.2f}s — marking task failed")
        return True
    return False


if __name__ == "__main__":
    task = TaskState()
    print("Task started, heartbeat fresh.")

    # Simulate the task's own loop freezing (e.g. waiting on a dead socket)
    # — nothing inside the task calls task.beat() again after this point.
    time.sleep(0.3)

    # An external sweep, on its own schedule, is the only thing that can
    # notice. Threshold is tiny here just to make the demo finish fast.
    external_liveness_sweep(task, stale_after_seconds=0.2)
    print(f"Final status: {task.status}")
