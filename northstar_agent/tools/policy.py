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
    "findstr",
    "get-childitem",
    "get-content",
    "head",
    "ls",
    "pwd",
    "tail",
    "type",
    "where",
    "wc",
    "whoami",
}

BLOCKED_PATTERNS = (
    (r"\bsudo\b", "Privilege escalation is blocked."),
    (r"\bcurl\b", "Network downloads are blocked."),
    (r"\bwget\b", "Network downloads are blocked."),
    (r"\binvoke-webrequest\b", "Network downloads are blocked."),
    (r"\bchmod\b", "Permission changes are blocked."),
    (r"\bchown\b", "Ownership changes are blocked."),
    (r"\|.*(?:sh|bash|zsh|cmd|powershell)\b", "Piping directly into a shell is blocked."),
)

APPROVAL_REQUIRED_PATTERNS = (
    (r"\brm\b", "Deleting files requires approval."),
    (r"\bdel\b", "Deleting files requires approval."),
    (r"\bremove-item\b", "Deleting files requires approval."),
    (r"\bmv\b", "Moving files requires approval."),
    (r"\bmove-item\b", "Moving files requires approval."),
    (r"\bkill\b", "Stopping processes requires approval."),
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


@dataclass(slots=True)
class PendingApprovalStore:
    """Persistent store for approvals waiting on a YES or NO response."""

    path: Path

    def load(self) -> dict[str, dict[str, str]]:
        if self.path.exists():
            return json.loads(self.path.read_text(encoding="utf-8"))
        return {}

    def save(self, pending: dict[str, dict[str, str]]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(pending, indent=2), encoding="utf-8")

    def set(self, thread_id: str, approval: dict[str, str]) -> None:
        pending = self.load()
        pending[thread_id] = approval
        self.save(pending)

    def remove(self, thread_id: str) -> dict[str, str] | None:
        pending = self.load()
        approval = pending.pop(thread_id, None)
        self.save(pending)
        return approval


def command_signature(command: str) -> str:
    """Normalize command approvals under a stable signature."""

    return f"command::{command.strip()}"


def delete_signature(relative_path: str) -> str:
    """Normalize delete approvals under a stable signature."""

    return f"delete::{relative_path.strip()}"


def inspect_command(command: str, store: ApprovalStore) -> dict[str, str]:
    """Return a detailed decision for a command."""

    stripped = command.strip()
    signature = command_signature(stripped)
    if not stripped:
        return {
            "status": "blocked",
            "reason": "Empty commands are blocked.",
            "signature": signature,
        }

    base_command = stripped.split()[0].lower()
    if base_command in SAFE_COMMANDS:
        return {
            "status": "safe",
            "reason": "Read-only command on the safe allowlist.",
            "signature": signature,
        }

    if store.is_allowed(signature):
        return {
            "status": "approved",
            "reason": "Previously approved command.",
            "signature": signature,
        }

    lowered = stripped.lower()
    for pattern, reason in BLOCKED_PATTERNS:
        if re.search(pattern, lowered):
            return {"status": "blocked", "reason": reason, "signature": signature}

    for pattern, reason in APPROVAL_REQUIRED_PATTERNS:
        if re.search(pattern, lowered):
            return {"status": "needs_approval", "reason": reason, "signature": signature}

    return {
        "status": "needs_approval",
        "reason": "Command is not on the safe allowlist.",
        "signature": signature,
    }


def classify_command(command: str, store: ApprovalStore) -> str:
    """Classify a command as safe, previously approved, or approval-gated."""

    return inspect_command(command, store)["status"]
