# Northstar Agent

Northstar Agent is a self-hosted workspace agent for developers. It remembers context across sessions, works through a simple local API, and takes local actions only inside a configured workspace with explicit approval for risky operations.

## Why this exists

Most agent demos are either vague chatbots or oversized platforms. Northstar is intentionally smaller: one runtime, one workspace, one clear safety model.

It is built for people who want a hackable local agent that can:
- inspect files in a workspace
- remember project context and user preferences
- run local commands with approval gates
- stay usable through a plain HTTP interface, with Telegram available as an optional second surface

## What it does well

- Session memory in SQLite so conversations survive restarts
- Rolling summaries so long chats stay within context limits
- Long-term memory stored as editable markdown files
- Workspace-scoped file tools for reading, writing, and deleting files
- Approval-gated local command execution
- One shared runtime exposed through HTTP and Telegram

## Primary workflow

The main product surface is the local HTTP API.

1. Start the agent
2. Send a chat request
3. Inspect the response
4. Approve or deny risky actions when needed

Telegram is supported for the same runtime, but HTTP is the fastest way to understand and demo the project.

## Quickstart

### Requirements

- Python 3.10+
- OpenAI API key
- Telegram bot token only if you want Telegram mode

### Install

```bash
pip install -r requirements.txt
```

### Configure

Create a `.env` file in the repo root or copy from `.env.example`.

```env
OPENAI_API_KEY=your_openai_api_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
NORTHSTAR_MODE=http
NORTHSTAR_MODEL=gpt-4o
NORTHSTAR_HOST=0.0.0.0
NORTHSTAR_PORT=8080
NORTHSTAR_STORAGE_DIR=storage
NORTHSTAR_WORKSPACE_DIR=workspace
NORTHSTAR_SUMMARY_THRESHOLD=10
```

### Run

```bash
python main.py
```

### Use the HTTP API

Health check:

```bash
curl http://localhost:8080/health
```

Chat with the agent:

```bash
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d "{\"user_id\":\"atlas\",\"message\":\"list the files in my workspace\"}"
```

Approve a pending action:

```bash
curl -X POST http://localhost:8080/approve \
  -H "Content-Type: application/json" \
  -d "{\"user_id\":\"atlas\",\"decision\":\"YES\"}"
```

Inspect pending approvals:

```bash
curl http://localhost:8080/pending/atlas
```

Inspect all pending approvals:

```bash
curl http://localhost:8080/pending
```

Inspect recent activity:

```bash
curl "http://localhost:8080/activity?limit=10"
```

Inspect saved memories:

```bash
curl http://localhost:8080/memories
```

## Example workflows

### 1. Inspect a workspace

Ask:

```text
List the files in my workspace and tell me what looks important.
```

Northstar can inspect the workspace tree and read project files before answering.

### 2. Keep working memory between sessions

Ask:

```text
Remember that this repo uses SQLite for session memory and Telegram is optional.
```

Northstar can persist durable notes in markdown files under `storage/memory/`.

### 3. Run local actions with approval

Ask:

```text
Run a command to show me the current directory contents.
```

If the command is safe, it runs immediately. If it is risky or unknown, the agent creates a pending approval and waits for a `YES` or `NO`.

## How it works

```text
HTTP request or Telegram message
  -> shared Northstar runtime
  -> LangGraph state machine
  -> model call
  -> workspace tools / memory tools / approval flow
  -> SQLite session state + markdown long-term memory
```

## Project layout

```text
main.py
northstar_agent/
  config.py
  core/
    agent.py
    identity.py
    memory.py
  interfaces/
    api.py
    telegram_bot.py
  prompts/
    identity.md
    tools.md
  tools/
    policy.py
    registry.py
storage/
workspace/
tests/
```

`legacy/` contains archived prototype files and is not part of the active product surface.

## Modes

- `http`: recommended default for local development and demos
- `telegram`: run the Telegram bot only
- `both`: run HTTP and Telegram together on the same runtime

If your Telegram account has a username, using the same value as `user_id` in HTTP lets both interfaces talk to the same thread.

## Storage

- `storage/sessions.db`: session checkpoints and summaries
- `storage/exec-approvals.json`: remembered approval decisions
- `storage/pending-approvals.json`: approvals waiting for a YES or NO
- `storage/activity.jsonl`: append-only runtime activity log
- `storage/memory/*.md`: long-term memory notes
- `workspace/`: sandboxed file operations root

## Verification

Run the current lightweight checks:

```bash
python -m unittest discover -s tests
python -m compileall main.py northstar_agent tests
```
