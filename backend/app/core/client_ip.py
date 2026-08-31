"""Resolve the visitor's address as it survives the proxy chain.

Production chain:

    visitor -> Vercel edge -> Caddy -> this container

Vercel does forward the visitor's address, but **Caddy destroys it**: with no
``trusted_proxies`` configured, it treats its direct peer as the client and
REPLACES ``X-Forwarded-For`` with the Vercel edge address. That address rotates
between requests (35.182.251.83, 15.156.206.244, 3.96.159.140 observed on
2026-08-31), so any limit keyed on it lands in a different bucket every time and
counts nothing at all.

``X-Vercel-Forwarded-For`` crosses Caddy untouched, since Caddy does not know
that header. It is therefore the one carrying the visitor's address.

Accepted limitation: on the API domain, reachable without going through Vercel,
a caller can forge these headers. The safeguards that still hold there are the
ones that depend on no header — the live-sandbox ceiling and the global spend
budget.
"""

from fastapi import Request

_HEADERS = ("x-vercel-forwarded-for", "x-forwarded-for")


def visitor_address(request: Request) -> str:
    for name in _HEADERS:
        raw = request.headers.get(name)
        if not raw:
            continue
        first = raw.split(",")[0].strip()
        if first:
            return first

    return request.client.host if request.client else "unknown"
