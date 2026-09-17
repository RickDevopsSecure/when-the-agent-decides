"""Pattern 10 — A one-time validation is not a boundary.

Checking a target's IP once, when a request is first accepted, leaves a
window open: a redirect or a DNS-rebind can change what the system actually
connects to afterward. This pattern re-validates on every hop and pins the
connection to the exact IP that was validated, closing the gap between
"checked" and "used".

Pattern 5 in this repo (environment-defensive execution) is the same idea
applied to subprocess PATH resolution; this is the network-scope version.
"""

from __future__ import annotations

import ipaddress
from dataclasses import dataclass


class ScopeViolation(Exception):
    pass


def is_authorized_public_ip(ip: str) -> bool:
    addr = ipaddress.ip_address(ip)
    return not (addr.is_private or addr.is_loopback or addr.is_link_local
                or addr.is_reserved or addr.is_multicast or addr.is_unspecified)


@dataclass
class ValidatedHop:
    hostname: str
    ip: str


def front_door_check_only(hostname: str, resolve) -> ValidatedHop:
    """The bug: valid at t=0, but nothing stops the connection from later
    landing somewhere else entirely (redirect, DNS-rebind)."""
    ip = resolve(hostname)
    if not is_authorized_public_ip(ip):
        raise ScopeViolation(f"{hostname} resolved to out-of-scope IP {ip}")
    return ValidatedHop(hostname, ip)  # <-- this IP is never checked again


def revalidate_every_hop(hostname: str, resolve) -> ValidatedHop:
    """The fix: re-run the exact same check at the moment of actual use,
    and pin the connection to that freshly-validated IP — not to whatever
    was true earlier."""
    ip = resolve(hostname)
    if not is_authorized_public_ip(ip):
        raise ScopeViolation(f"{hostname} resolved to out-of-scope IP {ip} at connect-time")
    return ValidatedHop(hostname, ip)


if __name__ == "__main__":
    # A hostname that resolves differently the second time (simulating a
    # DNS-rebind attack): public IP at t=0, internal metadata-adjacent IP at t=1.
    responses = iter(["8.8.8.8", "169.254.169.254"])

    def rebinding_dns(_hostname: str) -> str:
        return next(responses)

    hop_t0 = front_door_check_only("example.test", rebinding_dns)
    print(f"t=0 front-door check passed: {hop_t0}")

    try:
        revalidate_every_hop("example.test", rebinding_dns)
    except ScopeViolation as e:
        print(f"t=1 re-validation caught it: {e}")
