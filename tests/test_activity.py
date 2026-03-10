import tempfile
import unittest
from pathlib import Path

from northstar_agent.core.activity import ActivityLog
from northstar_agent.core.memory import list_memory_entries, save_memory_entry


class ActivityTests(unittest.TestCase):
    def test_activity_log_returns_recent_events(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            log = ActivityLog(Path(temp_dir) / "activity.jsonl")
            log.append("approval_requested", {"thread_id": "user:atlas"})
            log.append("memory_saved", {"key": "project-notes"})

            events = log.recent(limit=2)

        self.assertEqual(len(events), 2)
        self.assertEqual(events[0]["event"], "approval_requested")
        self.assertEqual(events[1]["payload"]["key"], "project-notes")

    def test_memory_entries_are_structured(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            memory_dir = Path(temp_dir) / "memory"
            save_memory_entry(memory_dir, "Project Notes", "Northstar stores memory on disk.")

            entries = list_memory_entries(memory_dir)

        self.assertEqual(entries[0]["key"], "project-notes")
        self.assertIn("Northstar", entries[0]["content"])


if __name__ == "__main__":
    unittest.main()
