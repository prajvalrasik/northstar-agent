"""LangChain tool definitions plus approval-aware runtime helpers."""

from __future__ import annotations

import subprocess
from pathlib import Path

from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode

from .policy import (
    ApprovalStore,
    classify_command,
    command_signature,
    delete_signature,
)


class ToolRuntime:
    """Owns pending approvals, workspace sandboxing, and command execution."""

    def __init__(self, workspace_dir: Path, approvals_file: Path):
        self.workspace_dir = workspace_dir
        self.approval_store = ApprovalStore(approvals_file)
        self.pending_approvals: dict[str, dict[str, str]] = {}
        self._current_thread_id = ""

    def set_current_thread_id(self, thread_id: str) -> None:
        self._current_thread_id = thread_id

    def get_current_thread_id(self) -> str:
        return self._current_thread_id

    def tool_node(self, tools):
        return ToolNode(tools)

    def _resolve_workspace_path(self, relative_path: str) -> Path:
        candidate = (self.workspace_dir / relative_path).resolve()
        candidate.relative_to(self.workspace_dir.resolve())
        return candidate

    def get_pending(self, thread_id: str):
        pending = self.pending_approvals.get(thread_id)
        return dict(pending) if pending else None

    def queue_pending(self, thread_id: str, pending: dict[str, str]) -> None:
        self.pending_approvals[thread_id] = pending

    def resolve_pending(self, thread_id: str, decision: str) -> str:
        pending = self.pending_approvals.get(thread_id)
        if not pending:
            return "No pending approval for this user."

        approved = decision.strip().upper() == "YES"
        signature = pending["signature"]

        if not approved:
            self.approval_store.remember(signature, approved=False)
            del self.pending_approvals[thread_id]
            return f"Denied: {pending['display']}"

        self.approval_store.remember(signature, approved=True)
        del self.pending_approvals[thread_id]

        if pending["kind"] == "command":
            result = subprocess.run(
                pending["target"],
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(self.workspace_dir),
            )
            output = (result.stdout + result.stderr).strip()
            return output or "(no output)"

        path = self._resolve_workspace_path(pending["target"])
        if not path.exists():
            return f"File '{pending['target']}' not found."

        path.unlink()
        return f"Deleted '{pending['target']}' from the workspace."


def build_workspace_tools(runtime: ToolRuntime):
    """Create workspace and command tools bound to the runtime."""

    def _resolve(relative_path: str) -> Path:
        try:
            return runtime._resolve_workspace_path(relative_path)
        except ValueError as exc:
            raise ValueError("Path must stay inside the configured workspace.") from exc

    @tool
    def list_workspace_files() -> str:
        """List files under the configured workspace."""

        files = []
        for path in sorted(runtime.workspace_dir.rglob("*")):
            relative = path.relative_to(runtime.workspace_dir)
            suffix = "/" if path.is_dir() else ""
            files.append(f"{relative}{suffix}")
        return "\n".join(files) if files else "Workspace is empty."

    @tool
    def read_workspace_file(path: str) -> str:
        """Read a UTF-8 text file inside the workspace."""

        file_path = _resolve(path)
        if not file_path.exists() or not file_path.is_file():
            return f"File '{path}' not found in the workspace."
        return file_path.read_text(encoding="utf-8")

    @tool
    def write_workspace_file(path: str, content: str) -> str:
        """Write UTF-8 text to a file inside the workspace."""

        file_path = _resolve(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
        return f"Wrote '{path}' in the workspace."

    @tool
    def delete_workspace_file(path: str) -> str:
        """Delete a file inside the workspace after user approval."""

        thread_id = runtime.get_current_thread_id()
        file_path = _resolve(path)
        if not file_path.exists() or not file_path.is_file():
            return f"File '{path}' not found in the workspace."

        signature = delete_signature(path)
        if runtime.approval_store.is_allowed(signature):
            file_path.unlink()
            return f"Deleted '{path}' from the workspace."

        runtime.queue_pending(
            thread_id,
            {
                "kind": "delete",
                "target": path,
                "signature": signature,
                "display": f"delete {path}",
            },
        )
        return (
            f"Approval required before deleting '{path}'. "
            "Reply YES to confirm or NO to cancel."
        )

    @tool
    def run_command(command: str) -> str:
        """Run a shell command from the configured workspace."""

        thread_id = runtime.get_current_thread_id()
        command = command.strip()
        safety = classify_command(command, runtime.approval_store)

        if safety in {"safe", "approved"}:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(runtime.workspace_dir),
            )
            output = (result.stdout + result.stderr).strip()
            return output or "(no output)"

        runtime.queue_pending(
            thread_id,
            {
                "kind": "command",
                "target": command,
                "signature": command_signature(command),
                "display": command,
            },
        )
        return (
            f"Approval required before running this command:\n{command}\n\n"
            "Reply YES to allow it or NO to deny it."
        )

    return [
        list_workspace_files,
        read_workspace_file,
        write_workspace_file,
        delete_workspace_file,
        run_command,
    ]
