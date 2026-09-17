"""Pattern 4 — Historical context is a hint, never a fact.

This is the exact bug documented in the paper, reduced to its smallest
possible form. The "bad" prompt builder below optimizes for saving time by
telling the model not to re-test what a previous run already confirmed. A
language model does not reliably distinguish between "this is already
known" and "I can claim this as my own" — so it ends up citing stale
findings as if they were fresh, and 6 out of 7 CRITICAL/HIGH findings in one
real run were exactly this.

The fix does not remove the historical context (it is still useful for
directing attention) — it changes what the model is allowed to do with it.
"""

from __future__ import annotations


def build_context_bad(prior_findings: list[str]) -> str:
    """The buggy version. Do not use — kept here only for contrast."""
    listing = "\n".join(f"- {f}" for f in prior_findings)
    return (
        "Known confirmed findings from previous runs:\n"
        f"{listing}\n\n"
        "Use this to focus your attention. Do not re-test what is already "
        "confirmed above."
    )


def build_context_fixed(prior_findings: list[str]) -> str:
    """The fix: same information, different license to act on it."""
    listing = "\n".join(f"- {f}" for f in prior_findings)
    return (
        "Historical context — NOT evidence from this run:\n"
        f"{listing}\n\n"
        "This is only a hint about where to look. If any of these is still "
        "live, confirm it with a real tool call producing fresh evidence "
        "before reporting it. If the tool fails or does not confirm it, do "
        "NOT report it just because it is listed above. Restating a past "
        "finding without new evidence is not counted as verified work."
    )


if __name__ == "__main__":
    prior = ["outdated CMS version", "debug mode enabled", "admin tokens in HTML source"]
    print("--- bad ---")
    print(build_context_bad(prior))
    print("\n--- fixed ---")
    print(build_context_fixed(prior))
