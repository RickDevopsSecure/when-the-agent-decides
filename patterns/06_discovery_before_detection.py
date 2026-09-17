"""Pattern 6 — Recall is won in discovery, not just in detection.

A confirmation engine that is never shown the vulnerable endpoint cannot
find it, no matter how good it is. This pattern shows the exact shape of the
fix: the SAME injection-confirmation function, unchanged, tested against
two different surface-discovery strategies. Widening discovery (parsing
HTML forms and same-origin links, not just API specs) is what moved recall
from zero to real confirmed findings — the detector never changed.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Candidate:
    url: str
    param: str


def discover_narrow(openapi_spec: dict) -> list[Candidate]:
    """The original discovery: only what an OpenAPI spec or a JS bundle
    happens to mention. Silently blind to server-rendered forms."""
    return [
        Candidate(path, param)
        for path, params in openapi_spec.get("paths", {}).items()
        for param in params
    ]


def discover_wide(openapi_spec: dict, html_forms: list[dict], same_origin_links: list[str]) -> list[Candidate]:
    """The fix: same OpenAPI parsing, PLUS form fields and same-origin
    ?param= links pulled straight from the rendered page."""
    candidates = discover_narrow(openapi_spec)
    for form in html_forms:
        for field in form.get("fields", []):
            candidates.append(Candidate(form["action"], field))
    for link in same_origin_links:
        if "?" in link and "=" in link:
            query = link.split("?", 1)[1]
            for pair in query.split("&"):
                if "=" in pair:
                    candidates.append(Candidate(link.split("?")[0], pair.split("=")[0]))
    return candidates


def confirm_injection(candidate: Candidate) -> bool:
    """The confirmation engine — deliberately unchanged between both runs.
    In the real case, this same function found nothing under narrow
    discovery and confirmed real SQLi/XSS under wide discovery, because the
    vulnerable parameter only ever appeared in a server-rendered form."""
    # Stand-in for a real confirmation (error-based / boolean / time-based).
    # The vulnerable param in this toy example only shows up via forms.
    return candidate.param == "search_query"


if __name__ == "__main__":
    spec = {"paths": {"/api/status": ["verbose"]}}
    forms = [{"action": "/search", "fields": ["search_query", "category"]}]
    links = ["/results?search_query=test&page=1"]

    narrow = discover_narrow(spec)
    wide = discover_wide(spec, forms, links)

    print(f"narrow discovery: {len(narrow)} candidate(s), "
          f"{sum(confirm_injection(c) for c in narrow)} confirmed")
    print(f"wide discovery:   {len(wide)} candidate(s), "
          f"{sum(confirm_injection(c) for c in wide)} confirmed")
