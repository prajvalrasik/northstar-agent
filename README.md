# Northstar Agent

Northstar Agent is a lightweight autonomous assistant for personal operations and project support. It combines a shared agent core with persistent memory, approval-gated local actions, and two equal interfaces: a FastAPI service and a Telegram bot.

## What it does

- Maintains session memory in SQLite so conversations survive restarts.
- Compacts long chats into a rolling summary to keep context usable.
- Stores durable notes and preferences in a file-backed long-term memory layer.
- Reads and writes files inside a configured workspace.
- Runs safe shell commands immediately and sends risky ones through an approval flow.
- Exposes the same agent runtime through HTTP and Telegram.

## Architecture

```text
HTTP API ----\
              > shared Northstar runtime -> LangGraph -> model + tools
Telegram ----/                               |            |
                                              |            +-> workspace tools
                                              |            +-> shell approval flow
                                              |
                                              +-> SQLite session memory
                                              +-> file-backed long-term memory
```

## Project Layout

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
  memory/
workspace/
legacy/
tests/
```

`legacy/` contains the original experimental scripts that were archived during the repo cleanup. The active product surface is the `northstar_agent` package and `main.py`.

## Requirements

- Python 3.10+
- OpenAI API key
- Telegram bot token if you enable Telegram mode

Install dependencies:

```bash
pip install -r requirements.txt
```

## Environment

Create a `.env` file in the repo root or copy from `.env.example`.

```env
OPENAI_API_KEY=your_openai_api_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
NORTHSTAR_MODE=both
NORTHSTAR_MODEL=gpt-4o
NORTHSTAR_HOST=0.0.0.0
NORTHSTAR_PORT=8080
NORTHSTAR_STORAGE_DIR=storage
NORTHSTAR_WORKSPACE_DIR=workspace
NORTHSTAR_SUMMARY_THRESHOLD=10
```

### Runtime modes

- `http`: start only the FastAPI service
- `telegram`: start only the Telegram bot
- `both`: start both interfaces with one shared agent runtime

## Running

Start the app:

```bash
python main.py
```

### HTTP usage

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

Check pending approvals:

```bash
curl http://localhost:8080/pending/atlas
```

Example `/chat` response:

```json
{
  "response": "Approval required before running this command:\ndir\n\nReply YES to allow it or NO to deny it.",
  "pending_approval": {
    "kind": "command",
    "target": "dir",
    "signature": "command::dir",
    "display": "dir"
  }
}
```

### Telegram usage

- Create a bot with BotFather and place the token in `.env`.
- Start `python main.py` with `NORTHSTAR_MODE=telegram` or `both`.
- Message the bot normally.
- Reply `YES` or `NO` when the agent asks for approval on a destructive action.

If your Telegram account has a username, that username becomes your shared identity. Using the same value as `user_id` in the HTTP API lets both interfaces talk to the same memory thread.

## Storage

- `storage/sessions.db`: SQLite checkpoints for session memory and summaries
- `storage/exec-approvals.json`: remembered approvals and denials
- `storage/memory/*.md`: long-term memory notes
- `workspace/`: sandboxed file operation root for agent tools

## Verification

Run lightweight checks:

```bash
python -m unittest discover -s tests
python -m compileall main.py northstar_agent tests
```
