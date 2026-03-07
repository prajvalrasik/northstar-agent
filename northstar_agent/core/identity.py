"""Identity helpers shared across interfaces."""

from __future__ import annotations


def build_thread_id(identity: str) -> str:
    """Normalize a user identity into a shared thread identifier."""

    cleaned = identity.strip().lower().replace(" ", "-")
    if not cleaned:
        raise ValueError("Identity must not be empty.")
    return f"user:{cleaned}"
