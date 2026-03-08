import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from northstar_agent.config import ROOT_DIR, load_config


class ConfigTests(unittest.TestCase):
    def test_load_config_uses_defaults(self):
        with mock.patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=True):
            config = load_config()

        self.assertEqual(config.mode, "both")
        self.assertEqual(config.model_name, "gpt-4o")
        self.assertEqual(config.storage_dir, (ROOT_DIR / "storage").resolve())
        self.assertEqual(
            config.pending_approvals_file,
            (ROOT_DIR / "storage" / "pending-approvals.json").resolve(),
        )
        self.assertEqual(config.workspace_dir, (ROOT_DIR / "workspace").resolve())

    def test_custom_paths_are_resolved(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = Path(temp_dir) / "state"
            workspace = Path(temp_dir) / "work"
            env = {
                "OPENAI_API_KEY": "test-key",
                "NORTHSTAR_STORAGE_DIR": str(storage),
                "NORTHSTAR_WORKSPACE_DIR": str(workspace),
                "NORTHSTAR_MODE": "http",
            }
            with mock.patch.dict(os.environ, env, clear=True):
                config = load_config()

        self.assertEqual(config.storage_dir, storage.resolve())
        self.assertEqual(config.memory_dir, (storage / "memory").resolve())
        self.assertEqual(config.workspace_dir, workspace.resolve())


if __name__ == "__main__":
    unittest.main()
