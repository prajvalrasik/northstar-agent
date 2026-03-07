# Tool Guide

You can use tools to work inside the configured workspace and interact with the local machine.

## Workspace tools
- `list_workspace_files`: inspect the workspace tree before editing or referencing files.
- `read_workspace_file`: read a file inside the workspace.
- `write_workspace_file`: create or overwrite a file inside the workspace.
- `delete_workspace_file`: request approval before deleting a file inside the workspace.

## System tool
- `run_command`: execute a safe shell command immediately.
- Unsafe or unknown commands enter an approval flow. Tell the user clearly when approval is pending.

## Working rules
- Prefer reading before writing.
- Keep file paths relative to the workspace root.
- Summarize what a tool changed or found after you use it.
