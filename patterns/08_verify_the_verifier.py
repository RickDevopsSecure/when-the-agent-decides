"""Pattern 8 — The verifier needs verifying too.

A test harness checked that every mandatory phase had run, against a
reference list maintained BY HAND inside the harness. As the real pipeline
gained and lost phases, that list drifted, and the gate kept reporting
success regardless of what actually ran — a tautological check.

The fix: the harness's notion of "what should run" is derived from the same
place the runtime gets it from, never a hand-maintained parallel copy.
"""

from __future__ import annotations


# --- The bug, preserved for contrast -------------------------------------

_HAND_MAINTAINED_EXPECTED_PHASES = ["recon", "injection", "access_control"]
# ^ Someone added "auth_flow" to the real pipeline last month. Nobody
#   remembered to update this list. The gate below will pass forever.


def buggy_gate(phases_that_ran: list[str]) -> bool:
    return set(phases_that_ran) >= set(_HAND_MAINTAINED_EXPECTED_PHASES)


# --- The fix --------------------------------------------------------------

class Pipeline:
    """The one real source of truth for "what phases exist"."""
    REGISTERED_PHASES = ["recon", "injection", "access_control", "auth_flow"]


def sound_gate(phases_that_ran: list[str], pipeline: type[Pipeline] = Pipeline) -> bool:
    """Derives the expected set from the same place the runtime derives its
    own phase list — there is no second copy to drift out of sync."""
    expected = set(pipeline.REGISTERED_PHASES)
    return set(phases_that_ran) >= expected


if __name__ == "__main__":
    ran = ["recon", "injection", "access_control"]  # auth_flow silently never ran

    print("buggy_gate  :", "PASS" if buggy_gate(ran) else "FAIL",
          "(wrong: auth_flow is missing and nobody notices)")
    print("sound_gate  :", "PASS" if sound_gate(ran) else "FAIL",
          "(correct: catches the real gap because it reads the live phase list)")
