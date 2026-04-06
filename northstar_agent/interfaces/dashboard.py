"""Minimal local dashboard for Northstar Agent."""

from __future__ import annotations


def render_dashboard_html() -> str:
    """Return the single-page dashboard markup."""

    return """<!doctype html>
<html lang="en" data-theme="light">
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
    [data-theme="dark"] {
      --bg: #1a1a14;
      --panel: #23231a;
      --ink: #e8e2d4;
      --muted: #9a9488;
      --line: #38352b;
      --accent: #4a9e82;
      --accent-2: #e09a4a;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: Georgia, "Times New Roman", serif;
      color: var(--ink);
      background: var(--bg);
      transition: background 0.2s, color 0.2s;
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
    .hero-top {
      display: flex;
      align-items: baseline;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 12px;
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
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 18px;
      box-shadow: 0 12px 30px rgba(31, 31, 25, 0.06);
      transition: background 0.2s, border-color 0.2s;
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
      background: rgba(255, 255, 255, 0.08);
      color: var(--ink);
      transition: background 0.2s, border-color 0.2s;
    }
    [data-theme="light"] input,
    [data-theme="light"] textarea {
      background: rgba(255, 255, 255, 0.92);
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
      transition: opacity 0.15s;
    }
    button:hover { opacity: 0.85; }
    button.secondary {
      background: var(--accent-2);
    }
    button.ghost {
      background: transparent;
      border: 1px solid var(--line);
      color: var(--ink);
      font-size: 0.88rem;
      padding: 7px 14px;
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
      background: rgba(255, 255, 255, 0.04);
      white-space: pre-wrap;
      overflow-wrap: anywhere;
      transition: background 0.2s;
    }
    [data-theme="light"] .output,
    [data-theme="light"] .list {
      background: rgba(255, 255, 255, 0.58);
    }
    .output {
      font-family: Georgia, serif;
      line-height: 1.65;
    }
    .output code {
      font-family: "Courier New", monospace;
      background: rgba(0,0,0,0.07);
      padding: 1px 5px;
      border-radius: 4px;
      font-size: 0.9em;
    }
    [data-theme="dark"] .output code {
      background: rgba(255,255,255,0.1);
    }
    .output strong { font-weight: 700; }
    .output em { font-style: italic; }
    .list {
      min-height: 200px;
    }
    .item {
      padding: 12px 0;
      border-bottom: 1px solid rgba(216, 207, 191, 0.4);
    }
    [data-theme="dark"] .item {
      border-bottom-color: rgba(56, 53, 43, 0.7);
    }
    .item:last-child {
      border-bottom: 0;
      padding-bottom: 0;
    }
    .meta {
      color: var(--muted);
      font-size: 0.88rem;
    }
    .event-badge {
      display: inline-block;
      font-size: 0.75rem;
      font-weight: 700;
      letter-spacing: 0.04em;
      padding: 2px 8px;
      border-radius: 999px;
      margin-bottom: 4px;
      text-transform: uppercase;
    }
    .badge-agent_turn      { background: #d0e8d9; color: #1a5c32; }
    .badge-memory_saved    { background: #dce4f5; color: #1a3a7a; }
    .badge-approval_requested { background: #fde8c8; color: #7a3a00; }
    .badge-approval_granted   { background: #d0e8d9; color: #1a5c32; }
    .badge-approval_denied    { background: #f5d8d8; color: #7a1a1a; }
    .badge-command_executed   { background: #e8e0f5; color: #3a1a7a; }
    .badge-command_blocked    { background: #f5d8d8; color: #7a1a1a; }
    .badge-file_deleted       { background: #f5e8d8; color: #7a4a00; }
    [data-theme="dark"] .badge-agent_turn      { background: #1a3d28; color: #7ecc9f; }
    [data-theme="dark"] .badge-memory_saved    { background: #1a2a4a; color: #7ea8f0; }
    [data-theme="dark"] .badge-approval_requested { background: #4a2e10; color: #f0aa60; }
    [data-theme="dark"] .badge-approval_granted   { background: #1a3d28; color: #7ecc9f; }
    [data-theme="dark"] .badge-approval_denied    { background: #4a1a1a; color: #f08080; }
    [data-theme="dark"] .badge-command_executed   { background: #2a1a4a; color: #b080f0; }
    [data-theme="dark"] .badge-command_blocked    { background: #4a1a1a; color: #f08080; }
    [data-theme="dark"] .badge-file_deleted       { background: #4a2e10; color: #f0aa60; }
    .live-dot {
      display: inline-block;
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: var(--accent);
      margin-right: 6px;
      animation: pulse 2s infinite;
    }
    @keyframes pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.3; }
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
      <div class="hero-top">
        <div class="eyebrow">Local control panel</div>
        <button class="ghost" id="theme-toggle" type="button">Dark mode</button>
      </div>
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
          <h2 style="margin-top:16px">Response</h2>
          <div id="chat-output" class="output">No request sent yet.</div>
        </div>

        <div class="panel">
          <h2><span class="live-dot"></span>Recent activity</h2>
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
    // ── Theme ──────────────────────────────────────────────────────────────────
    const root = document.documentElement;
    const themeBtn = document.getElementById('theme-toggle');

    function applyTheme(theme) {
      root.setAttribute('data-theme', theme);
      themeBtn.textContent = theme === 'dark' ? 'Light mode' : 'Dark mode';
    }

    function toggleTheme() {
      const next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      localStorage.setItem('ns-theme', next);
      applyTheme(next);
    }

    applyTheme(localStorage.getItem('ns-theme') || 'light');

    function escapeHtml(value) {
      return String(value)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
    }

    // ── Markdown-lite renderer ─────────────────────────────────────────────────
    function renderMarkdown(text) {
      return escapeHtml(text)
        .replace(/`([^`]+)`/g, '<code>$1</code>')
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.+?)\*/g, '<em>$1</em>')
        .replace(/\n/g, '<br>');
    }

    // ── Event badge ────────────────────────────────────────────────────────────
    function eventBadge(eventType) {
      const cls = 'event-badge badge-' + eventType.replace(/[^a-z_]/g, '_');
      return `<span class="${cls}">${eventType.replace(/_/g, ' ')}</span>`;
    }

    function formatPayload(event) {
      const p = event.payload || {};
      const parts = [];
      if (p.display)         parts.push(escapeHtml(p.display));
      if (p.command)         parts.push('<code>' + escapeHtml(p.command) + '</code>');
      if (p.key)             parts.push('key: ' + escapeHtml(p.key));
      if (p.message_preview) parts.push(escapeHtml(p.message_preview));
      if (p.path)            parts.push(escapeHtml(p.path));
      if (p.reason)          parts.push('<em>' + escapeHtml(p.reason) + '</em>');
      return parts.join(' &middot; ') || '';
    }

    // ── DOM refs ───────────────────────────────────────────────────────────────
    const chatForm    = document.getElementById('chat-form');
    const userIdInput = document.getElementById('user-id');
    const messageInput = document.getElementById('message');
    const chatOutput  = document.getElementById('chat-output');
    const pendingList = document.getElementById('pending-list');
    const activityList = document.getElementById('activity-list');
    const memoryList  = document.getElementById('memory-list');
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
          <strong>${escapeHtml(pending.display)}</strong>
          <div class="meta">${escapeHtml(threadId)} &middot; ${escapeHtml(pending.reason)}</div>
          <div class="actions">
            <button type="button" data-thread-id="${escapeHtml(threadId)}" data-decision="YES">Approve</button>
            <button type="button" class="secondary" data-thread-id="${escapeHtml(threadId)}" data-decision="NO">Deny</button>
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
          ${eventBadge(event.event)}
          <div class="meta">${event.timestamp}</div>
          <div>${formatPayload(event)}</div>
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
          <strong>${escapeHtml(memory.key)}</strong>
          <div>${renderMarkdown(memory.content)}</div>
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

    themeBtn.addEventListener('click', toggleTheme);

    pendingList.addEventListener('click', (event) => {
      const button = event.target.closest('button[data-thread-id]');
      if (!button) {
        return;
      }
      resolveApproval(button.dataset.threadId, button.dataset.decision).catch(() => {});
    });

    // ── SSE live updates ───────────────────────────────────────────────────────
    function connectSSE() {
      const es = new EventSource('/events');
      es.onmessage = (e) => {
        try {
          const data = JSON.parse(e.data);
          renderActivity(data);
          // Also refresh pending in case an approval was auto-resolved
          fetchJson('/pending').then(renderPending).catch(() => {});
        } catch (_) {}
      };
      es.onerror = () => {
        es.close();
        setTimeout(connectSSE, 5000);
      };
    }

    connectSSE();

    // ── Chat ───────────────────────────────────────────────────────────────────
    chatForm.addEventListener('submit', async (event) => {
      event.preventDefault();
      chatOutput.innerHTML = '<em>Thinking...</em>';
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
        let html = renderMarkdown(data.response || '');
        if (data.pending_approval) {
          html += '<br><br><strong>Pending approval:</strong> ' + escapeHtml(data.pending_approval.display);
        }
        chatOutput.innerHTML = html;
        await refreshPanels();
      } catch (error) {
        chatOutput.textContent = String(error);
      }
    });

    refreshButton.addEventListener('click', () => refreshPanels().catch(() => {}));
    refreshPanels().catch(() => {});
  </script>
</body>
</html>"""
