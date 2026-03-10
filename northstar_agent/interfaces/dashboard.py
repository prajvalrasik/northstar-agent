"""Minimal local dashboard for Northstar Agent."""

from __future__ import annotations


def render_dashboard_html() -> str:
    """Return the single-page dashboard markup."""

    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Northstar Agent</title>
  <style>
    :root {
      --bg: #f4efe6;
      --panel: #fffaf0;
      --ink: #1f1f19;
      --muted: #6f6a5f;
      --line: #d8cfbf;
      --accent: #215b4a;
      --accent-2: #d0873a;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: Georgia, "Times New Roman", serif;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, #efe3cb 0, transparent 24rem),
        linear-gradient(180deg, #f8f4ec 0%, var(--bg) 100%);
    }
    .shell {
      max-width: 1180px;
      margin: 0 auto;
      padding: 32px 20px 48px;
    }
    .hero {
      display: grid;
      gap: 18px;
      margin-bottom: 28px;
    }
    .eyebrow {
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: var(--accent);
      font-size: 0.78rem;
      font-weight: 700;
    }
    h1 {
      margin: 0;
      font-size: clamp(2.3rem, 5vw, 4.8rem);
      line-height: 0.95;
    }
    .lede {
      max-width: 760px;
      color: var(--muted);
      font-size: 1.05rem;
      line-height: 1.6;
    }
    .layout {
      display: grid;
      grid-template-columns: 1.4fr 1fr;
      gap: 18px;
    }
    .panel {
      background: color-mix(in srgb, var(--panel) 94%, white 6%);
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 18px;
      box-shadow: 0 12px 30px rgba(31, 31, 25, 0.06);
    }
    .stack {
      display: grid;
      gap: 18px;
    }
    .panel h2 {
      margin: 0 0 12px;
      font-size: 1.1rem;
    }
    .panel p {
      margin: 0 0 12px;
      color: var(--muted);
    }
    form {
      display: grid;
      gap: 12px;
    }
    label {
      display: grid;
      gap: 6px;
      font-size: 0.92rem;
    }
    input, textarea, button {
      font: inherit;
    }
    input, textarea {
      width: 100%;
      padding: 12px 14px;
      border-radius: 12px;
      border: 1px solid var(--line);
      background: rgba(255, 255, 255, 0.92);
      color: var(--ink);
    }
    textarea {
      min-height: 150px;
      resize: vertical;
    }
    button {
      border: 0;
      border-radius: 999px;
      padding: 11px 16px;
      background: var(--accent);
      color: white;
      cursor: pointer;
    }
    button.secondary {
      background: var(--accent-2);
    }
    .button-row {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
    }
    .output, .list {
      min-height: 120px;
      padding: 14px;
      border-radius: 14px;
      border: 1px dashed var(--line);
      background: rgba(255, 255, 255, 0.58);
      white-space: pre-wrap;
      overflow-wrap: anywhere;
    }
    .list {
      min-height: 200px;
    }
    .item {
      padding: 12px 0;
      border-bottom: 1px solid rgba(216, 207, 191, 0.7);
    }
    .item:last-child {
      border-bottom: 0;
      padding-bottom: 0;
    }
    .meta {
      color: var(--muted);
      font-size: 0.88rem;
    }
    .actions {
      display: flex;
      gap: 8px;
      margin-top: 10px;
      flex-wrap: wrap;
    }
    .empty {
      color: var(--muted);
      font-style: italic;
    }
    @media (max-width: 900px) {
      .layout {
        grid-template-columns: 1fr;
      }
    }
  </style>
</head>
<body>
  <div class="shell">
    <section class="hero">
      <div class="eyebrow">Local control panel</div>
      <h1>Northstar Agent</h1>
      <div class="lede">
        A self-hosted workspace agent for developers. Chat with the runtime,
        inspect pending approvals, review recent activity, and browse long-term
        memories from one local page.
      </div>
    </section>

    <section class="layout">
      <div class="stack">
        <div class="panel">
          <h2>Chat</h2>
          <p>Use the same API-backed runtime the project exposes publicly.</p>
          <form id="chat-form">
            <label>
              User ID
              <input id="user-id" name="user_id" value="atlas" />
            </label>
            <label>
              Message
              <textarea id="message" name="message">List the files in my workspace and tell me what matters.</textarea>
            </label>
            <div class="button-row">
              <button type="submit">Send message</button>
              <button class="secondary" type="button" id="refresh-all">Refresh panels</button>
            </div>
          </form>
          <h2>Response</h2>
          <div id="chat-output" class="output">No request sent yet.</div>
        </div>

        <div class="panel">
          <h2>Recent activity</h2>
          <div id="activity-list" class="list"><div class="empty">No events yet.</div></div>
        </div>
      </div>

      <div class="stack">
        <div class="panel">
          <h2>Pending approvals</h2>
          <div id="pending-list" class="list"><div class="empty">No pending approvals.</div></div>
        </div>

        <div class="panel">
          <h2>Saved memories</h2>
          <div id="memory-list" class="list"><div class="empty">No saved memories yet.</div></div>
        </div>
      </div>
    </section>
  </div>

  <script>
    const chatForm = document.getElementById('chat-form');
    const userIdInput = document.getElementById('user-id');
    const messageInput = document.getElementById('message');
    const chatOutput = document.getElementById('chat-output');
    const pendingList = document.getElementById('pending-list');
    const activityList = document.getElementById('activity-list');
    const memoryList = document.getElementById('memory-list');
    const refreshButton = document.getElementById('refresh-all');

    async function fetchJson(url, options) {
      const response = await fetch(url, options);
      if (!response.ok) {
        const text = await response.text();
        throw new Error(text || response.statusText);
      }
      return response.json();
    }

    function renderPending(data) {
      const entries = Object.entries(data.pending_approvals || {});
      if (!entries.length) {
        pendingList.innerHTML = '<div class="empty">No pending approvals.</div>';
        return;
      }

      pendingList.innerHTML = entries.map(([threadId, pending]) => `
        <div class="item">
          <strong>${pending.display}</strong>
          <div class="meta">${threadId} · ${pending.reason}</div>
          <div class="actions">
            <button type="button" onclick="resolveApproval('${threadId}', 'YES')">Approve</button>
            <button type="button" class="secondary" onclick="resolveApproval('${threadId}', 'NO')">Deny</button>
          </div>
        </div>
      `).join('');
    }

    function renderActivity(data) {
      const events = data.events || [];
      if (!events.length) {
        activityList.innerHTML = '<div class="empty">No events yet.</div>';
        return;
      }

      activityList.innerHTML = events.slice().reverse().map((event) => `
        <div class="item">
          <strong>${event.event}</strong>
          <div class="meta">${event.timestamp}</div>
          <div>${JSON.stringify(event.payload)}</div>
        </div>
      `).join('');
    }

    function renderMemories(data) {
      const memories = data.memories || [];
      if (!memories.length) {
        memoryList.innerHTML = '<div class="empty">No saved memories yet.</div>';
        return;
      }

      memoryList.innerHTML = memories.map((memory) => `
        <div class="item">
          <strong>${memory.key}</strong>
          <div>${memory.content}</div>
        </div>
      `).join('');
    }

    async function refreshPanels() {
      const [pending, activity, memories] = await Promise.all([
        fetchJson('/pending'),
        fetchJson('/activity?limit=12'),
        fetchJson('/memories'),
      ]);
      renderPending(pending);
      renderActivity(activity);
      renderMemories(memories);
    }

    async function resolveApproval(threadId, decision) {
      const userId = threadId.replace(/^user:/, '');
      await fetchJson('/approve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId, decision }),
      });
      await refreshPanels();
    }

    window.resolveApproval = resolveApproval;

    chatForm.addEventListener('submit', async (event) => {
      event.preventDefault();
      chatOutput.textContent = 'Thinking...';
      try {
        const payload = {
          user_id: userIdInput.value.trim(),
          message: messageInput.value,
        };
        const data = await fetchJson('/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
        const sections = [data.response];
        if (data.pending_approval) {
          sections.push('\\nPending approval: ' + JSON.stringify(data.pending_approval));
        }
        chatOutput.textContent = sections.join('\\n');
        await refreshPanels();
      } catch (error) {
        chatOutput.textContent = String(error);
      }
    });

    refreshButton.addEventListener('click', refreshPanels);
    refreshPanels().catch((error) => {
      chatOutput.textContent = String(error);
    });
  </script>
</body>
</html>"""
