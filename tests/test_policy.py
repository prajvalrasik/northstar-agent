import tempfile
import unittest
from pathlib import Path

from northstar_agent.tools.policy import (
    ApprovalStore,
    classify_command,
    command_signature,
    delete_signature,
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

    def test_preapproved_command_is_reused(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ApprovalStore(Path(temp_dir) / "approvals.json")
            signature = command_signature("python app.py")
            store.remember(signature, approved=True)
            self.assertEqual(classify_command("python app.py", store), "approved")

    def test_delete_signature_is_stable(self):
        self.assertEqual(delete_signature("notes/todo.md"), "delete::notes/todo.md")


if __name__ == "__main__":
    unittest.main()
