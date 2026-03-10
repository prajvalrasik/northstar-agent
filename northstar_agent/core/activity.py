"""Append-only activity logging for operator visibility."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


class ActivityLog:
    """Persist newline-delimited activity events."""

    def __init__(self, path: Path):
        self.path = path

    def append(self, event_type: str, payload: dict[str, object]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": event_type,
            "payload": payload,
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event) + "\n")

    def recent(self, limit: int = 50) -> list[dict[str, object]]:
        if not self.path.exists():
            return []

        with self.path.open("r", encoding="utf-8") as handle:
            events = [json.loads(line) for line in handle if line.strip()]

        if limit <= 0:
            return []
        return events[-limit:]
