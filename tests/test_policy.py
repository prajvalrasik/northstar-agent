import tempfile
import unittest
from pathlib import Path

from northstar_agent.tools.policy import (
    ApprovalStore,
    PendingApprovalStore,
    classify_command,
    command_signature,
    delete_signature,
    inspect_command,
)


class PolicyTests(unittest.TestCase):
    def test_safe_command_is_allowed_immediately(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ApprovalStore(Path(temp_dir) / "approvals.json")
            self.assertEqual(classify_command("dir", store), "safe")

    def test_unknown_command_needs_approval(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ApprovalStore(Path(temp_dir) / "approvals.json")
            self.assertEqual(classify_command("python manage.py migrate", store), "needs_approval")

    def test_blocked_command_is_reported(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ApprovalStore(Path(temp_dir) / "approvals.json")
            details = inspect_command("curl https://example.com", store)
            self.assertEqual(details["status"], "blocked")
            self.assertIn("blocked", details["reason"].lower())

    def test_preapproved_command_is_reused(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ApprovalStore(Path(temp_dir) / "approvals.json")
            signature = command_signature("python app.py")
            store.remember(signature, approved=True)
            self.assertEqual(classify_command("python app.py", store), "approved")

    def test_windows_safe_alias_is_allowlisted(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ApprovalStore(Path(temp_dir) / "approvals.json")
            details = inspect_command("Get-ChildItem", store)
            self.assertEqual(details["status"], "safe")

    def test_pending_approvals_persist(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            store = PendingApprovalStore(Path(temp_dir) / "pending.json")
            pending = {
                "kind": "command",
                "target": "dir",
                "signature": command_signature("dir"),
                "display": "dir",
                "reason": "Read-only command on the safe allowlist.",
                "status": "pending",
            }
            store.set("user:atlas", pending)

            reloaded = store.load()
            self.assertEqual(reloaded["user:atlas"]["target"], "dir")

            removed = store.remove("user:atlas")
            self.assertEqual(removed["signature"], command_signature("dir"))
            self.assertEqual(store.load(), {})

    def test_delete_signature_is_stable(self):
        self.assertEqual(delete_signature("notes/todo.md"), "delete::notes/todo.md")


if __name__ == "__main__":
    unittest.main()
