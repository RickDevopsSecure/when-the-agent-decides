"""Pattern 2 — Adversarial verification, not optional.

An agent that reports its own findings with no one else questioning them has
a structural conflict of interest. This pattern shows the minimal shape of a
fix: a verification pass runs on a separate call, receives no access to the
original agent's reasoning trace, and requires a positive fresh-evidence
signal before a finding is allowed to reach the report. Absence of that
signal is a discard, not a pass.

In the field case behind this repository, 6 of 7 CRITICAL/HIGH findings from
one run were discarded by exactly this kind of pass, because they were
restated from a previous run without new evidence.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Confidence = Literal["confirmed", "discarded"]


@dataclass
class ProposedFinding:
    title: str
    severity: str
    evidence: str          # what the *current* run actually observed
    cites_prior_run: bool   # true if the agent referenced historical context


@dataclass
class VerificationResult:
    finding: ProposedFinding
    confidence: Confidence
    reason: str


def verify(finding: ProposedFinding) -> VerificationResult:
    """Runs with no visibility into the agent's chain of thought — only the
    finding's own stated evidence. This is the whole point: a verifier that
    can see the original reasoning tends to just agree with it."""
    has_fresh_evidence = bool(finding.evidence) and not finding.cites_prior_run

    if has_fresh_evidence:
        return VerificationResult(finding, "confirmed", "evidence produced this run")

    return VerificationResult(
        finding,
        "discarded",
        "no fresh evidence — finding is a restatement of prior context, not a new observation",
    )


def verify_batch(findings: list[ProposedFinding]) -> list[VerificationResult]:
    return [verify(f) for f in findings]


if __name__ == "__main__":
    batch = [
        ProposedFinding("outdated framework in production", "CRITICAL",
                         evidence="", cites_prior_run=True),
        ProposedFinding("reflected XSS on /search", "HIGH",
                         evidence="payload echoed unescaped in response body", cites_prior_run=False),
    ]
    for result in verify_batch(batch):
        print(f"[{result.confidence.upper():9}] {result.finding.title} — {result.reason}")
