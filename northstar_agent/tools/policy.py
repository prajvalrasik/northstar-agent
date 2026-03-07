"""Approval persistence and command safety policy."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path


SAFE_COMMANDS = {
    "cat",
    "date",
    "dir",
    "echo",
    "head",
    "ls",
    "pwd",
    "tail",
    "type",
    "wc",
    "whoami",
}

DANGEROUS_PATTERNS = (
    r"\brm\b",
    r"\bdel\b",
    r"\bremove-item\b",
    r"\bsudo\b",
    r"\bchmod\b",
    r"\bchown\b",
    r"\bmv\b",
    r"\bmove-item\b",
    r"\bkill\b",
    r"\bcurl\b",
    r"\bwget\b",
    r"\|.*sh\b",
)


@dataclass(slots=True)
class ApprovalStore:
    """Persistent allow/deny store for commands and destructive actions."""

    path: Path

    def load(self) -> dict[str, list[str]]:
        if self.path.exists():
            return json.loads(self.path.read_text(encoding="utf-8"))
        return {"allowed": [], "denied": []}

    def save(self, approvals: dict[str, list[str]]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(approvals, indent=2), encoding="utf-8")

    def is_allowed(self, signature: str) -> bool:
        return signature in self.load()["allowed"]

    def remember(self, signature: str, approved: bool) -> None:
        approvals = self.load()
        key = "allowed" if approved else "denied"
        if signature not in approvals[key]:
            approvals[key].append(signature)
        self.save(approvals)


def command_signature(command: str) -> str:
    """Normalize command approvals under a stable signature."""

    return f"command::{command.strip()}"


def delete_signature(relative_path: str) -> str:
    """Normalize delete approvals under a stable signature."""

    return f"delete::{relative_path.strip()}"


def classify_command(command: str, store: ApprovalStore) -> str:
    """Classify a command as safe, previously approved, or approval-gated."""

    stripped = command.strip()
    if not stripped:
        return "needs_approval"

    base_command = stripped.split()[0].lower()
    if base_command in SAFE_COMMANDS:
        return "safe"

    signature = command_signature(stripped)
    if store.is_allowed(signature):
        return "approved"

    lowered = stripped.lower()
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, lowered):
            return "needs_approval"

    return "needs_approval"
