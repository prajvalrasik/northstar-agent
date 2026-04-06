# Northstar Agent

A local AI agent that reads your workspace, remembers context across sessions, and runs commands... but only with your approval.

Most agent tools either just chat or run autonomously without asking. Northstar sits in the middle: it can browse files, remember project notes, and execute shell commands, but risky actions always pause for a YES/NO before anything happens. Everything runs on your machine. No cloud storage, no subscriptions.

![Northstar Agent dashboard](./NorthStar%20Snapshot.png)

---

## What it does

- **Reads and writes files** inside a sandboxed workspace directory
- **Searches across files** to find what you're looking for
- **Runs shell commands** safe ones immediately, risky ones only after you approve
- **Remembers things** across sessions, stored as plain markdown files you can edit
- **Keeps conversation history** in SQLite so context survives restarts
- **Local dashboard** at `localhost:8080` with chat, pending approvals, activity log, and memory browser

Supported LLM providers: OpenAI and Anthropic (Claude).

---

## Setup

**Requirements:** Python 3.10+, an OpenAI or Anthropic API key

```bash
git clone https://github.com/prajvalrasik/northstar-agent
cd northstar-agent

python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

Copy the example config and fill in your key:

```bash
cp .env.example .env
```

Open `.env` and set `OPENAI_API_KEY` (or `ANTHROPIC_API_KEY` if using Claude). Change `NORTHSTAR_PROVIDER` to `anthropic` if needed. Everything else can stay as-is to start.

Run it:

```bash
python main.py
```

Open `http://localhost:8080` in your browser.

---

## Using the dashboard

Once running, the dashboard gives you:

- A chat panel to talk to the agent
- A live pending approvals list — approve or deny directly from the browser
- A recent activity feed that updates automatically
- A memory browser showing what the agent has saved

You can also use the HTTP API directly:

```bash
# Chat
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "atlas", "message": "list the files in my workspace"}'

# Approve a pending action
curl -X POST http://localhost:8080/approve \
  -H "Content-Type: application/json" \
  -d '{"user_id": "atlas", "decision": "YES"}'

# Check what's pending
curl http://localhost:8080/pending

# Recent activity
curl "http://localhost:8080/activity?limit=10"

# Saved memories
curl http://localhost:8080/memories
```

---

## How approvals work

When you ask the agent to do something risky like... deleting a file, running an unknown command, it pauses and queues an approval instead of acting immediately. You see it in the dashboard and click Approve or Deny. If you approve, the decision is remembered so you won't be asked again for the same action.

Safe commands (like `ls`, `pwd`) run immediately. Network commands, privilege escalation, and shell piping are blocked entirely regardless of approval.

---

## Configuration

| Variable | Default | Description |
|---|---|---|
| `NORTHSTAR_PROVIDER` | `openai` | LLM provider: `openai` or `anthropic` |
| `OPENAI_API_KEY` | — | Required if provider is `openai` |
| `ANTHROPIC_API_KEY` | — | Required if provider is `anthropic` |
| `NORTHSTAR_MODEL` | `gpt-4o` | Model name (e.g. `claude-sonnet-4-5`) |
| `NORTHSTAR_MODE` | `http` | `http`, `telegram`, or `both` |
| `TELEGRAM_BOT_TOKEN` | — | Required if mode includes `telegram` |
| `NORTHSTAR_HOST` | `0.0.0.0` | HTTP bind address |
| `NORTHSTAR_PORT` | `8080` | HTTP port |
| `NORTHSTAR_WORKSPACE_DIR` | `workspace` | Directory the agent can read/write |
| `NORTHSTAR_STORAGE_DIR` | `storage` | Where sessions, memory, and logs are stored |
| `NORTHSTAR_SUMMARY_THRESHOLD` | `10` | Messages before rolling summary kicks in |

---

## Telegram

Set `NORTHSTAR_MODE=telegram` or `both` and add your `TELEGRAM_BOT_TOKEN`. The same approval flow works over Telegram — reply YES or NO to approve or deny actions. If your Telegram username matches the `user_id` you use in HTTP, both interfaces share the same conversation thread.

---

## Storage layout

```
storage/
  sessions.db            # conversation history (SQLite)
  memory/                # long-term notes as markdown files
  activity.jsonl         # append-only event log
  exec-approvals.json    # remembered approve/deny decisions
  pending-approvals.json # approvals waiting for a response
workspace/               # sandboxed directory for file operations
```

---

## Running tests

```bash
python -m unittest discover -s tests
```

---

## Project layout

```
main.py
northstar_agent/
  config.py
  core/
    agent.py       # LangGraph state machine, LLM setup
    memory.py      # long-term memory helpers
    identity.py    # thread ID management
    activity.py    # event logging
  interfaces/
    api.py         # FastAPI routes + SSE
    dashboard.py   # single-page local UI
    telegram_bot.py
  tools/
    registry.py    # workspace and command tools
    policy.py      # command safety rules and approval store
  prompts/
    identity.md
    tools.md
storage/
workspace/
tests/
```
