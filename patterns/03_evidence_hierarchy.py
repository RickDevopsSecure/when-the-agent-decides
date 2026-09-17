"""Pattern 3 — Evidence hierarchy.

Not every "confirmed finding" an AI security agent produces carries the same
evidentiary weight. This pattern ranks confirmation techniques by how hard
they are to false-positive, and refuses to let two techniques of different
tiers share the same report label.

The out-of-band network callback tier deserves special note: when the
target itself makes an outbound request to a unique, single-use domain
generated for that specific probe, the proof is self-contained. It requires
no interpretation from the model at all — either the network traffic
happened, or it didn't.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum


class EvidenceTier(IntEnum):
    """Ordered from least to most trustworthy. The int value doubles as a
    rough false-positive-risk score for sorting a report."""
    TEXT_HEURISTIC = 1     # model infers a vuln from a response pattern
    TIMING_SIGNAL = 2      # latency delta between control and probe request
    TOOL_RERUN = 3         # a specialized binary reproduces the result independently
    OOB_CALLBACK = 4       # target made an outbound request to a single-use domain


TIER_LABEL = {
    EvidenceTier.TEXT_HEURISTIC: "heuristic (unverified)",
    EvidenceTier.TIMING_SIGNAL: "timing-based (probabilistic)",
    EvidenceTier.TOOL_RERUN: "tool-confirmed",
    EvidenceTier.OOB_CALLBACK: "network-confirmed",
}


@dataclass
class Finding:
    title: str
    tier: EvidenceTier

    @property
    def report_label(self) -> str:
        return TIER_LABEL[self.tier]


def sort_by_trust(findings: list[Finding]) -> list[Finding]:
    """Highest-trust evidence first — this is how a report should be read,
    not necessarily how it was discovered."""
    return sorted(findings, key=lambda f: f.tier, reverse=True)


if __name__ == "__main__":
    findings = [
        Finding("possible outdated component", EvidenceTier.TEXT_HEURISTIC),
        Finding("blind SQLi via response delay", EvidenceTier.TIMING_SIGNAL),
        Finding("SQL injection confirmed by injection engine", EvidenceTier.TOOL_RERUN),
        Finding("blind SSRF confirmed via OOB callback", EvidenceTier.OOB_CALLBACK),
    ]
    for f in sort_by_trust(findings):
        print(f"[{f.report_label:28}] {f.title}")
