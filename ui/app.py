from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sys
import traceback
from urllib.parse import urlparse


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from agent.brain import query_brain


HOST = "127.0.0.1"
PORT = 7860


HTML = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Second Brain</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #f7f5ef;
      --panel: #ffffff;
      --ink: #1e2421;
      --muted: #6c746f;
      --line: #dedbd2;
      --accent: #356f64;
      --accent-strong: #244e47;
      --accent-soft: #e2efeb;
      --gold: #b58a36;
      --danger: #a84032;
      --shadow: 0 18px 50px rgba(31, 35, 32, 0.12);
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      min-height: 100vh;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: var(--bg);
      color: var(--ink);
    }

    button, textarea {
      font: inherit;
    }

    .app {
      display: grid;
      grid-template-columns: 240px minmax(0, 1fr) 320px;
      min-height: 100vh;
    }

    .sidebar, .sources {
      background: #fbfaf6;
      border-color: var(--line);
      padding: 20px;
    }

    .sidebar {
      border-right: 1px solid var(--line);
      display: flex;
      flex-direction: column;
      gap: 22px;
    }

    .sources {
      border-left: 1px solid var(--line);
      overflow-y: auto;
    }

    .brand {
      display: flex;
      flex-direction: column;
      gap: 4px;
    }

    .brand h1 {
      margin: 0;
      font-size: 22px;
      line-height: 1.1;
      letter-spacing: 0;
    }

    .brand span, .label, .hint, .empty {
      color: var(--muted);
    }

    .nav {
      display: grid;
      gap: 8px;
    }

    .nav button, .action {
      min-height: 40px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
      color: var(--ink);
      cursor: pointer;
      transition: background 150ms ease, border 150ms ease, color 150ms ease;
    }

    .nav button {
      text-align: left;
      padding: 0 12px;
    }

    .nav button.active {
      border-color: var(--accent);
      background: var(--accent-soft);
      color: var(--accent-strong);
    }

    .status {
      margin-top: auto;
      display: grid;
      gap: 8px;
      color: var(--muted);
      font-size: 13px;
    }

    .status-dot {
      width: 8px;
      height: 8px;
      border-radius: 999px;
      background: var(--gold);
      display: inline-block;
      margin-right: 8px;
    }

    .main {
      display: grid;
      grid-template-rows: auto minmax(0, 1fr) auto;
      min-width: 0;
      height: 100vh;
    }

    .topbar {
      min-height: 72px;
      border-bottom: 1px solid var(--line);
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      padding: 0 24px;
      background: rgba(247, 245, 239, 0.86);
      backdrop-filter: blur(12px);
    }

    .topbar h2 {
      margin: 0;
      font-size: 18px;
      letter-spacing: 0;
    }

    .topbar p {
      margin: 4px 0 0;
      color: var(--muted);
      font-size: 13px;
    }

    .chat {
      overflow-y: auto;
      padding: 28px 24px;
    }

    .message-list {
      max-width: 880px;
      margin: 0 auto;
      display: grid;
      gap: 16px;
    }

    .message {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
      box-shadow: 0 8px 22px rgba(31, 35, 32, 0.06);
      padding: 16px;
    }

    .message.user {
      border-color: #cfd9d5;
      background: #f2f8f6;
    }

    .message.loading {
      color: var(--muted);
    }

    .message-header {
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 0.06em;
      margin-bottom: 8px;
      text-transform: uppercase;
    }

    .message-body {
      line-height: 1.58;
      white-space: pre-wrap;
    }

    .composer-wrap {
      border-top: 1px solid var(--line);
      padding: 16px 24px 20px;
      background: #fbfaf6;
    }

    .composer {
      max-width: 880px;
      margin: 0 auto;
      display: grid;
      grid-template-columns: minmax(0, 1fr) 96px;
      gap: 12px;
      align-items: end;
    }

    textarea {
      width: 100%;
      min-height: 58px;
      max-height: 180px;
      resize: vertical;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 14px;
      background: var(--panel);
      color: var(--ink);
      line-height: 1.4;
      outline: none;
    }

    textarea:focus {
      border-color: var(--accent);
      box-shadow: 0 0 0 3px rgba(53, 111, 100, 0.14);
    }

    .send {
      min-height: 58px;
      border: 0;
      border-radius: 8px;
      background: var(--accent);
      color: #ffffff;
      font-weight: 700;
      cursor: pointer;
    }

    .send:hover { background: var(--accent-strong); }
    .send:disabled { cursor: wait; opacity: 0.72; }

    .sources h2 {
      margin: 0 0 14px;
      font-size: 16px;
    }

    .source-list {
      display: grid;
      gap: 10px;
    }

    .source {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
      padding: 12px;
      display: grid;
      gap: 8px;
    }

    .source-title {
      font-weight: 700;
      line-height: 1.25;
      overflow-wrap: anywhere;
    }

    .source-meta {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
    }

    .pill {
      border: 1px solid #d7d1c3;
      border-radius: 999px;
      padding: 3px 8px;
      color: var(--muted);
      font-size: 12px;
      background: #fbfaf6;
    }

    .score {
      color: var(--accent-strong);
      font-weight: 700;
    }

    .error {
      color: var(--danger);
    }

    @media (max-width: 1050px) {
      .app {
        grid-template-columns: 220px minmax(0, 1fr);
      }
      .sources {
        display: none;
      }
    }

    @media (max-width: 720px) {
      .app {
        grid-template-columns: 1fr;
      }
      .sidebar {
        display: none;
      }
      .main {
        height: 100vh;
      }
      .topbar, .chat, .composer-wrap {
        padding-left: 14px;
        padding-right: 14px;
      }
      .composer {
        grid-template-columns: 1fr;
      }
      .send {
        min-height: 48px;
      }
    }
  </style>
</head>
<body>
  <div class="app">
    <aside class="sidebar">
      <div class="brand">
        <h1>Second Brain</h1>
        <span>Your notes, in conversation.</span>
      </div>
      <nav class="nav" aria-label="Workspace">
        <button class="active" type="button">Chat</button>
        <button type="button" disabled>Library</button>
        <button type="button" disabled>Indexing</button>
      </nav>
      <div class="status">
        <div><span class="status-dot"></span><span id="health">Checking backend</span></div>
        <div class="hint">Ask a question against your indexed Obsidian and Google Drive sources.</div>
      </div>
    </aside>

    <main class="main">
      <header class="topbar">
        <div>
          <h2>Research Chat</h2>
          <p>Answers are grounded in the local Chroma index and returned with citations.</p>
        </div>
        <button id="clear" class="action" type="button">Clear</button>
      </header>

      <section id="chat" class="chat" aria-live="polite">
        <div id="messages" class="message-list">
          <article class="message">
            <div class="message-header">Second Brain</div>
            <div class="message-body">Ask about your notes, courses, documents, or recurring ideas. I will bring the sources with the answer.</div>
          </article>
        </div>
      </section>

      <section class="composer-wrap">
        <form id="form" class="composer">
          <textarea id="question" placeholder="What do you want to understand from your notes?" autocomplete="off"></textarea>
          <button id="send" class="send" type="submit">Ask</button>
        </form>
      </section>
    </main>

    <aside class="sources">
      <h2>Sources</h2>
      <div id="sources" class="source-list">
        <div class="empty">Sources from the next answer will appear here.</div>
      </div>
    </aside>
  </div>

  <script>
    const form = document.querySelector("#form");
    const input = document.querySelector("#question");
    const send = document.querySelector("#send");
    const messages = document.querySelector("#messages");
    const chat = document.querySelector("#chat");
    const sources = document.querySelector("#sources");
    const clear = document.querySelector("#clear");
    const health = document.querySelector("#health");

    function escapeHtml(value) {
      return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
    }

    function addMessage(role, text, className = "") {
      const article = document.createElement("article");
      article.className = `message ${className}`.trim();
      article.innerHTML = `
        <div class="message-header">${escapeHtml(role)}</div>
        <div class="message-body">${escapeHtml(text)}</div>
      `;
      messages.append(article);
      chat.scrollTop = chat.scrollHeight;
      return article;
    }

    function renderSources(items) {
      if (!items || !items.length) {
        sources.innerHTML = '<div class="empty">No sources returned for this answer.</div>';
        return;
      }
      sources.innerHTML = items.map((item) => `
        <article class="source">
          <div class="source-title">${escapeHtml(item.file_name || "unknown")}</div>
          <div class="source-meta">
            <span class="pill">${escapeHtml(item.source || "source")}</span>
            <span class="pill">${escapeHtml(item.course || "-")}</span>
            <span class="pill">${escapeHtml(item.semester || "-")}</span>
          </div>
          <div class="pill score">Score ${Number(item.score || 0).toFixed(2)}</div>
        </article>
      `).join("");
    }

    async function checkHealth() {
      try {
        const response = await fetch("/health");
        if (!response.ok) throw new Error("Health check failed");
        health.textContent = "Backend ready";
      } catch {
        health.textContent = "Backend unavailable";
      }
    }

    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const question = input.value.trim();
      if (!question || send.disabled) return;

      addMessage("You", question, "user");
      input.value = "";
      send.disabled = true;
      send.textContent = "Asking";
      const loading = addMessage("Second Brain", "Searching your notes...", "loading");

      try {
        const response = await fetch("/api/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ question }),
        });
        const payload = await response.json();
        if (!response.ok) throw new Error(payload.error || "Request failed");

        loading.remove();
        addMessage("Second Brain", payload.answer || "No answer returned.");
        renderSources(payload.sources);
      } catch (error) {
        loading.remove();
        addMessage("Error", error.message, "error");
      } finally {
        send.disabled = false;
        send.textContent = "Ask";
        input.focus();
      }
    });

    input.addEventListener("keydown", (event) => {
      if (event.key === "Enter" && (event.metaKey || event.ctrlKey)) {
        form.requestSubmit();
      }
    });

    clear.addEventListener("click", () => {
      messages.innerHTML = "";
      renderSources([]);
      addMessage("Second Brain", "New thread ready.");
      input.focus();
    });

    checkHealth();
  </script>
</body>
</html>
"""


class SecondBrainHandler(BaseHTTPRequestHandler):
    def _send_json(self, status_code, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self):
        body = HTML.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/":
            self._send_html()
            return
        if path == "/health":
            self._send_json(200, {"ok": True})
            return
        self._send_json(404, {"error": "Not found"})

    def do_POST(self):
        path = urlparse(self.path).path
        if path != "/api/chat":
            self._send_json(404, {"error": "Not found"})
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            question = str(payload.get("question", "")).strip()
            if not question:
                self._send_json(400, {"error": "Question is required"})
                return

            result = query_brain(question)
            self._send_json(200, result)
        except Exception as exc:
            traceback.print_exc()
            self._send_json(500, {"error": str(exc)})

    def log_message(self, format, *args):
        print("%s - %s" % (self.address_string(), format % args))


def run(host=HOST, port=PORT):
    server = ThreadingHTTPServer((host, port), SecondBrainHandler)
    print(f"Second Brain UI running at http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down Second Brain UI")
    finally:
        server.server_close()


if __name__ == "__main__":
    run()
