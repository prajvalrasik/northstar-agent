"""Long-term memory helpers."""

from __future__ import annotations

import re
from pathlib import Path


def load_all_memories(memory_dir: Path) -> str:
    """Return all long-term memory files as a single formatted string."""

    if not memory_dir.exists():
        return ""

    memories: list[str] = []
    for file_path in sorted(memory_dir.glob("*.md")):
        content = file_path.read_text(encoding="utf-8").strip()
        if content:
            memories.append(f"[{file_path.stem}]\n{content}")
    return "\n\n".join(memories)


def save_memory_entry(memory_dir: Path, key: str, content: str) -> str:
    """Persist a memory entry and return the sanitized key used on disk."""

    safe_key = re.sub(r"[^a-zA-Z0-9_-]+", "-", key.strip()).strip("-").lower()
    if not safe_key:
        safe_key = "memory-note"

    memory_dir.mkdir(parents=True, exist_ok=True)
    (memory_dir / f"{safe_key}.md").write_text(content.strip(), encoding="utf-8")
    return safe_key


def search_memories(memory_dir: Path, query: str) -> str:
    """Find memory entries containing any word from the query."""

    if not memory_dir.exists():
        return "No long-term memory exists yet."

    terms = [term for term in query.lower().split() if term]
    if not terms:
        return "Provide at least one search term."

    matches: list[str] = []
    for file_path in sorted(memory_dir.glob("*.md")):
        content = file_path.read_text(encoding="utf-8")
        lowered = content.lower()
        if any(term in lowered for term in terms):
            matches.append(f"[{file_path.stem}]\n{content.strip()}")

    return "\n\n".join(matches) if matches else "No matching memories found."


def list_memory_entries(memory_dir: Path) -> list[dict[str, str]]:
    """Return long-term memory files as structured records."""

    if not memory_dir.exists():
        return []

    records: list[dict[str, str]] = []
    for file_path in sorted(memory_dir.glob("*.md")):
        records.append(
            {
                "key": file_path.stem,
                "content": file_path.read_text(encoding="utf-8").strip(),
            }
        )
    return records
