#!/usr/bin/env python3
"""
PyOS Dashboard (no-framework, fixed-port allocation, binds 0.0.0.0)
Run: python pyos_dashboard.py
Open dashboard: http://localhost:5000  (or forward port 5000 in Codespaces)
Type an app name (notepad, calculator, filemanager, terminal).
"""
import http.server
import socketserver
import socket
import threading
import subprocess
import urllib.parse
import html
import sys
import time

PORT = 5000
BASE_PORT = 6001       # first app port
MAX_APPS = 100         # max number of concurrent apps

APPS = {
    "notepad": "apps/notepad.py",
    "calculator": "apps/calculator.py",
    "filemanager": "apps/filemanager.py",
    "terminal": "apps/terminal.py",
}

HTML_TEMPLATE = """<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>PyOS Dashboard (no-framework)</title>
  <style>
    body {{ font-family: Arial, sans-serif; background: #121212; color: #eee; }}
    #main {{ width: 760px; margin: 30px auto; }}
    input[type=text] {{ width: 70%; padding: 10px; font-size: 16px; }}
    button {{ padding: 10px 14px; font-size: 16px; }}
    .msg {{ margin-top: 16px; padding: 10px; background: #222; border-radius: 6px; }}
    a {{ color: #7fc7ff; }}
    pre {{ background:#101010; padding:10px; border-radius:6px; }}
  </style>
</head>
<body>
  <div id="main">
    <h1>PyOS Dashboard (no-framework)</h1>
    <form method="POST" action="/">
      <input name="cmd" autofocus placeholder="Type command: notepad, calculator, filemanager, terminal" />
      <button type="submit">Run</button>
    </form>
    {resp_block}
    <hr/>
    <div><strong>Available apps:</strong></div>
    <ul>
      {apps_list}
    </ul>
    <div style="font-size:12px;color:#aaa;margin-top:10px;">
      Dashboard listening on <code>0.0.0.0:{port}</code>. Apps allocate from <code>{base}:{base_end}</code>.
      After launching an app, forward its port in Codespaces (Ports panel) or open http://localhost:PORT locally.
    </div>
    <h3>Active apps</h3>
    <pre>{active}</pre>
  </div>
</body>
</html>
"""

# simple sequential allocator
_alloc_index = 0
_active = {}  # app_name -> list of (pid, port, started_at)

def allocate_port():
    global _alloc_index
    if _alloc_index >= MAX_APPS:
        return None
    port = BASE_PORT + _alloc_index
    _alloc_index += 1
    return port

def launch_app(app_name):
    script = APPS.get(app_name)
    if not script:
        return None, "Unknown app"
    port = allocate_port()
    if port is None:
        return None, "No available ports"
    try:
        proc = subprocess.Popen([sys.executable, script, str(port)],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # give app a moment to start (non-blocking)
        time.sleep(0.15)
        # try to get pid
        pid = proc.pid
        _active.setdefault(app_name, []).append((pid, port, time.time()))
        print(f"[dashboard] Launched {app_name} pid={pid} port={port}")
        return port, None
    except Exception as e:
        return None, str(e)

class Handler(http.server.BaseHTTPRequestHandler):
    def _render(self, resp_block=""):
        apps_list = "\n".join(f"<li><b>{html.escape(k)}</b></li>" for k in APPS.keys())
        active_lines = []
        for name, entries in _active.items():
            for pid, port, ts in entries:
                active_lines.append(f"{name} pid={pid} port={port} started={time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ts))}")
        active_text = "\n".join(active_lines) or "(none)"
        body = HTML_TEMPLATE.format(resp_block=resp_block, apps_list=apps_list, port=PORT,
                                    base=BASE_PORT, base_end=BASE_PORT + MAX_APPS - 1, active=active_text)
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body.encode("utf-8"))))
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))

    def do_GET(self):
        self._render()

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8")
        data = urllib.parse.parse_qs(body)
        cmd = data.get("cmd", [""])[0].strip()
        resp_block = ""
        if cmd:
            if cmd in APPS:
                port, err = launch_app(cmd)
                if port:
                    # Note: in Codespaces/file-preview you must forward the port in the Ports panel.
                    link = f"http://localhost:{port}/"
                    resp_block = f'<div class="msg">Launched <b>{html.escape(cmd)}</b> on <a href="{html.escape(link)}" target="_blank">{html.escape(link)}</a><br/>If using Codespaces, forward port {port} in the Ports panel to open it in your browser.</div>'
                else:
                    resp_block = f'<div class="msg">Failed to launch <b>{html.escape(cmd)}</b>: {html.escape(err or "unknown")}</div>'
            else:
                resp_block = f'<div class="msg">Unknown command: <b>{html.escape(cmd)}</b></div>'
        else:
            resp_block = '<div class="msg">No command provided.</div>'
        self._render(resp_block=resp_block)

if __name__ == "__main__":
    # Print startup info to make forwarding easier
    print(f"Dashboard starting on 0.0.0.0:{PORT}")
    print(f"Apps will be allocated starting at {BASE_PORT} (up to {BASE_PORT + MAX_APPS -1})")
    with socketserver.ThreadingTCPServer(("0.0.0.0", PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("Shutting down dashboard")
            httpd.server_close()
